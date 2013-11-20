# -*- coding: utf-8 -*-  
"""
Starter Kit: Weather Station Demo
Copyright (C) 2013 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>

build_pkg.py: Package builder for Starter Kit: Weather Station Demo

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation; either version 2 
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

# Windows:
#   dependencies:
#       pythonxy (2.6)
#       py2exe
#       nsis
#       win redistributables vcredist under winxp
#   
#   run build scripts in all folders
#   run python build_pkg.py win to build the windows exe
#   final data is stored in folder "dist"
#
#   script copies OpenGL, special libs and plugin_system
#   in dist folder

import config

import sys
from distutils.core import setup
import os
import glob
import shutil
 
DESCRIPTION = 'Demo for the Starter Kit: Weather Station'
NAME = 'Starter Kit: Weather Station Demo'

def build_macosx_pkg():
    from setuptools import setup, find_packages

    PWD = os.path.dirname(os.path.realpath(__file__))
    RES_PATH = os.path.join(PWD, 'dist', 'Starter Kit Weather Station Demo.app', 'Contents', 'Resources')
    data_files = [
        ("../build_data/macos/", glob.glob(os.path.join(PWD, "../build_data/macos/", "*.nib"))),
        #('/usr/share/applications',['foo.desktop']),
    ]
    packages = find_packages()

    plist = dict(
        CFBundleName = 'Starter Kit Weather Station Demo',
        CFBundleShortVersionString = config.DEMO_VERSION,
        CFBundleGetInfoString = ' '.join(['Starter Kit: Weather Station Demo', config.DEMO_VERSION]),
        CFBundleExecutable = 'demo',
        CFBundleIdentifier = 'com.tinkerforge.starter_kit_weather_station_demo',
        CFBundleIconFile = 'demo-icon.icns',
        # hide dock icon
    #    LSUIElement = True,
    )

    additional_data_files = []
    def visitor(arg, dirname, names):
        for n in names:
            if os.path.isfile(os.path.join(dirname, n)):
                if arg[0] == 'y': # replace first folder name
                    additional_data_files.append((os.path.join(dirname.replace(arg[1],"")) , [os.path.join(dirname, n)]))
                else: # keep full path
                    additional_data_files.append((os.path.join(dirname), [os.path.join(dirname, n)]))
    
    os.path.walk(os.path.normcase("../build_data/macos/"), visitor, ('y',os.path.normcase("../build_data/macos/")))
    
    additional_data_files.append((os.path.join('.'), [os.path.join('.', 'demo-icon.png')]))

    additional_modules = []
    for f in os.listdir('tinkerforge'):
        if f.endswith('.py'):
            additional_modules.append('tinkerforge.' + f[:-3])

    def delete_old():
        BUILD_PATH = os.path.join(PWD, "build")
        DIST_PATH = os.path.join(PWD, "dist")
        if os.path.exists(BUILD_PATH):
            shutil.rmtree(BUILD_PATH)
        if os.path.exists(DIST_PATH):
            shutil.rmtree(DIST_PATH)

    def create_app():
        apps = [
            {
                "script" : "demo.py",
                "plist" : plist,
            }
        ]

        OPTIONS = {'argv_emulation' : True,
                   'iconfile' : '../build_data/macos/demo-icon.icns',
                   'site_packages' : True,
                   'includes' : ["atexit",
                                 "sip",
                                 "PyQt4.QtCore",
                                 "PyQt4.QtGui"
                                ] + additional_modules,
                   'excludes' : ['scipy',
                                 'distutils',
                                 'setuptools',
                                 'email',
                                 "OpenGL.GL",
                                 "PyQt4.QtOpenGL",
                                 "PyQt4.QtSvg",
                                 "PyQt4.Qwt5",
                                 'PyQt4.QtDeclarative',
                                 'PyQt4.QtDesigner',
                                 'PyQt4.QtHelp',
                                 'PyQt4.QtMultimedia',
                                 'PyQt4.QtNetwork',
                                 'PyQt4.QtScript',
                                 'PyQt4.QtScriptTools',
                                 'PyQt4.QtSql',
                                 'PyQt4.QtTest',
                                 'PyQt4.QtWebKit',
                                 'PyQt4.QtXml',
                                 'PyQt4.QtXmlPatterns']}

        data = data_files + additional_data_files

        setup(
            name = NAME,
            version = config.DEMO_VERSION,
            description = DESCRIPTION,
            author = 'Tinkerforge',
            author_email = 'info@tinkerforge.com',
            platforms = ["Mac OSX"],
            license = "GPL v2",
            url = "http://www.tinkerforge.com",
            scripts = ['demo.py'],
            app = apps,
            options = {'py2app': OPTIONS},
            # setup_requires = ['py2app'],
            data_files = data,
            packages = packages,
        )

    def qt_menu_patch():
        src = os.path.join(PWD, '../build_data/macos/', 'qt_menu.nib')
        dst = os.path.join(RES_PATH, 'qt_menu.nib')
        if not os.path.exists(dst):
            shutil.copytree(src, dst)

    _RUN_IN_TERM_PATCH = """import os
import sys

os.environ['RESOURCEPATH'] = os.path.dirname(os.path.realpath(__file__))

"""

    def run_in_term_patch():
        BOOT_FILE_PATH = os.path.join(RES_PATH, "__boot__.py")
        with open(BOOT_FILE_PATH) as f:
            old = f.read()

        new = _RUN_IN_TERM_PATCH + old

        with open(BOOT_FILE_PATH, 'w') as f:
            f.write(new)

    def data_files_patch():
        for item in data_files:
            if isinstance(item, tuple):
                folder_name = item[0]
            else:
                folder_name = item

            src = os.path.join(PWD, folder_name)
            dst = os.path.join(RES_PATH, folder_name)
            if not os.path.exists(dst):
                shutil.copytree(src, dst)

    ACTION_CREATE = len(sys.argv) == 3 and sys.argv[-1] == "build"

    if ACTION_CREATE:
        delete_old()
        create_app()
        qt_menu_patch()
        run_in_term_patch()
        data_files_patch()
    else:
        print "Usage: python setup.py py2app build"


def build_windows_pkg():
    PWD = os.path.dirname(os.path.realpath(__file__))
    BUILD_PATH = os.path.join(PWD, "build")
    DIST_PATH = os.path.join(PWD, "dist")
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)
    if os.path.exists(DIST_PATH):
        shutil.rmtree(DIST_PATH)

    import py2exe
    
    data_files = []
    def visitor(arg, dirname, names):
        for n in names:
            if os.path.isfile(os.path.join(dirname, n)):
                if arg[0] == 'y': # replace first folder name
                    data_files.append((os.path.join(dirname.replace(arg[1],"")) , [os.path.join(dirname, n)]))
                else: # keep full path
                    data_files.append((os.path.join(dirname) , [os.path.join(dirname, n)]))
    
    os.path.walk(os.path.normcase("../build_data/Windows/"), visitor, ('y', os.path.normcase("../build_data/Windows/")))
    
    data_files.append( ( os.path.join('.') , [os.path.join('.', 'demo-icon.png')] ) )

    additional_modules = []
    for f in os.listdir('tinkerforge'):
        if f.endswith('.py'):
            additional_modules.append('tinkerforge.' + f[:-3])

    setup(name = NAME,
          description = DESCRIPTION,
          version = config.DEMO_VERSION,
          data_files = data_files,
          options = {
                    "py2exe" : {
                    "dll_excludes" : ["MSVCP90.dll"],
                    "includes" : ["sip",
                                  "PyQt4.QtCore",
                                  "PyQt4.QtGui",] + additional_modules,
                    "excludes" : ["PyQt4.QtOpenGL",
                                  "PyQt4.QtSvg",
                                  "PyQt4.Qwt5",
                                  "OpenGL.GL",
                                  "config_linux",
                                  "config_macosx",
                                  "_gtkagg",
                                  "_tkagg",
                                  "Tkconstants",
                                  "Tkinter",
                                  "tcl",
                                  "pydoc",
                                  "email",
                                  "nose",
                                  "pdb",
                                  "inspect",
                                  "doctest",
                                  "difflib",
                                  "numpy.numarray",
                                  "numpy.oldnumeric",
                                  "numpy.core._dotblas",
                                  "numpy.random",
                                  "ctypes.macholib",
                                  "win32pdh",
                                  "win32ui"]
                    }
                    },
          zipfile = None,
          windows = [{'script' : 'demo.py', 'icon_resources' : [(0, os.path.normcase("../build_data/Windows/demo-icon.ico"))]}]
    )
    
    # build nsis
    lines = []
    for line in file('../build_data/Windows/nsis/demo_installer.nsi', 'rb').readlines():
        line = line.replace('<<DEMO_DOT_VERSION>>', config.DEMO_VERSION)
        line = line.replace('<<DEMO_UNDERSCORE_VERSION>>', config.DEMO_VERSION.replace('.', '_'))
        lines.append(line)
    file('dist/nsis/demo_installer.nsi', 'wb').writelines(lines)

    os.system('"C:\\Program Files\\NSIS\\makensis.exe" dist\\nsis\\demo_installer.nsi')


def build_linux_pkg():
    if os.geteuid() != 0:
        sys.stderr.write("build_pkg for Linux has to be started as root, exiting\n")
        sys.exit(1)

    src_path = os.getcwd()
    build_dir = 'build_data/linux/starter_kit_weather_station_demo/usr/share/starter_kit_weather_station_demo'
    dest_path = os.path.join(os.path.split(src_path)[0], build_dir)
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path)

    shutil.copytree(src_path, dest_path)
    
    build_data_path = os.path.join(os.path.split(src_path)[0], 'build_data/linux')
    os.chdir(build_data_path)

    STEXT = 'Version:'
    RTEXT = 'Version: {0}\n'.format(config.DEMO_VERSION)

    f = open('starter_kit_weather_station_demo/DEBIAN/control', 'r')
    lines = f.readlines()
    f.close()

    f = open('starter_kit_weather_station_demo/DEBIAN/control', 'w')
    for line in lines:
        if not line.find(STEXT) == -1:
            line = RTEXT
        f.write(line)
    f.close()

    os.system('chown -R root:root starter_kit_weather_station_demo/usr')
    os.system('dpkg -b starter_kit_weather_station_demo/ starter-kit-weather-station-demo-' + config.DEMO_VERSION + '_all.deb')
    os.system('chown -R `logname`:`logname` starter_kit_weather_station_demo/usr')


# call python build_pkg.py to build the windows/linux/macosx package
if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.argv = sys.argv[:1]

    if sys.platform.startswith('linux'):
        build_linux_pkg()
    elif sys.platform == 'win32':
        sys.argv.append('py2exe') # set sys.argv[1] for setup(), want to call py2exe
        build_windows_pkg()
    elif sys.platform == 'darwin':
        sys.argv.append('py2app') # set sys.argv[1] for setup(), want to call py2app
        sys.argv.append('build')
        build_macosx_pkg()
    else:
        print "error: unsupported platform: " + sys.platform
