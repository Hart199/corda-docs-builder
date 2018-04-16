#!/usr/bin/python

import os
import sys
import json
import shutil
import getopt
import subprocess

#
# Print help and die with specified return code
#
def help(exit) :
      print "metaBuilder.py -c <configFile>"
      sys.exit(exit)

def dbg (config, msg) :
    if config['verbose'] :
        print (msg)

def parseConfig (configFile) :
    with open (configFile, "r") as myfile:
        config = json.load (myfile)

        if "versions" not in config :
            print "Config file must specify versions to build"
            sys.exit(1)
        if "repo" not in config :
            print "Config file must specify repository to build"
            sys.exit(1)
        if "output" not in config :
            config["output"] = os.path.join(os.getcwd(), "build")

        return config

#
# build a specific tag
#
def buildVersion(config, version, tag) :
    os.chdir (os.path.join (config['output'], config['repo'][1]))

    # checkout the tag, should really check that this succeeds
    subprocess.call (["git", "checkout", tag])

    # build the docs
    subprocess.call (["./gradlew", "clean", "makedocs"])

    shutil.copytree(
            os.path.join(os.getcwd(), "docs", "build"),
            os.path.join(config['output'], version))

    os.chdir (config['output'])

#
# Main wrapper to clean up existing builds, checkout the source
# and drive individual builds of speicifc versions
#
def run(config) :
    if os.path.exists (config['output']) and config['clean'] :
        dbg(config, "Cleaning local build dir")
        shutil.rmtree(config['output'])

    if not os.path.exists (config['output']) :
        dbg(config, "Create output directory")
        os.makedirs(config['output'])

    os.chdir (config['output'])
    if not os.path.exists (os.path.join (config['output'], config['repo'][1])) :
        subprocess.call (["git", "clone", config['repo'][0], config['repo'][1]])

    for version, tag in config['versions'].iteritems() :
        buildVersion(config, version, tag)

#
# main driver, invoked by script entry
#
def main(argv) :
    try:
        opts, _ = getopt.getopt(argv,"hc:Cv",["configFile=","clean"])
    except getopt.GetoptError:
        help(2)

    configFile = "./conf.json"

    for opt, arg in opts:
        if opt == '-h': help(0)
        elif opt in ("-c", "--configFile") : configFile = arg
        elif opt in ("-C", "--clean") : clean = True
        elif opt in ("-v") : verbose = True

    # load *and* validate the config
    conf = parseConfig(configFile)

    # explicitly override whatever was set in the config file
    try :
        conf['clean'] = clean
    except UnboundLocalError :
        conf['clean'] = False

    try :
        conf['verbose'] = verbose
    except UnboundLocalError :
        conf['verbose'] = False

    # actually run the code
    run(conf)

#
# Script entry point
#
if __name__ == "__main__" :
    main(sys.argv[1:])
