[app]

# (str) Title of your application
title = 学习通作业提取

# (str) Package name
package.name = xxtdocx

# (str) Package domain (used for android/ios)
package.domain = com.liuwanwan1.xxtdocx

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all)
source.include_exts = py,png,jpg,kv,json,ttf

# (list) List of inclusions using pattern matching
source.include_patterns = img/*,answers/*

# (list) Source files to exclude
source.exclude_exts = spec

# (list) List of directory to exclude
source.exclude_dirs = tests,bin,venv,.git,.idea,.claude,__pycache__

# (list) List of exclusions using pattern matching
source.exclude_patterns = .gitignore,user.json,upload.py,logfile.log

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Note: pycryptodome may fail to build; if so, it will use pure Python fallback
requirements = python3,requests,beautifulsoup4,lxml,pycryptodome,qrcode,python-docx,rich,soupsieve,urllib3,certifi,charset-normalizer,idna,markdown-it-py,mdurl,pygments

# (str) Custom source folders for requirements
#p4a.source_dir =

# (list) Gust requirements
#osx.python_version = 3

# (list) Android requirements
android.requirements = kivy

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.apptheme = @android:style/Theme.NoTitleBar

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) Java classes to add as activities to the manifest.
#android.add_activities =

# (str) OUYA Console category
#android.ouya.category = GAME

# (str) Filename for OUYA Console icon
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML to include in the OUYA manifest
#android.ouya.manifest =

# (bool) Accept Android SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (int) Android SDK version
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (int) NDK API
android.ndk_api = 21

# (str) Target NDK version
android.ndk = 25b

# (str) Target SDK version
#android.sdk =

# (bool) Use the iOS or Android emulator
#android.emulator = False

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making big libs?
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
#android.arch = armeabi-v7a

# (int) overrides automatic versionCode computation
#android.numeric_version = 1

# (str) Android SDK directory
#android.sdk_path =

# (str) Android NDK directory
#android.ndk_path =

# (str) Android ANT directory
#android.ant_path =

# (bool) If True, then skip trying to update SDK/NDK/ANT
#android.skip_update = False

# (bool) If True, then use API29
#android.use_apk29 = False

# (str) bootstrap
#p4a.bootstrap = sdl2

# (str) python-for-android URL
#p4a.url =

# (str) python-for-android branch
#p4a.branch = develop

# (str) python-for-android fork
#p4a.fork =

# (str) python-for-android specific commit
#p4a.commit =

# (str) python-for-android local directory
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes
#p4a.local_recipes =

# (str) Filename of the python-for-android recipes
#p4a.recipes =

# (list) python-for-android extra params
#p4a.extra_args =

# (str) Setup.py for python-for-android
#p4a.setup_py =

# (str) Directory to put all project files
#p4a.project_dir =

# (str) Pyjnius version
#p4a.pyjnius_version =

# (str) Color depth
#android.color_depth = 32bit

# (bool) Let the app start full screen
android.fullscreen = 0

# (str) Orientation: one of landscape, portrait, all
android.orientation = portrait

# (int) Maximum API level
#android.maxapi = 31

# (bool) Private storage or not
#android.private_storage = True

# (str) Presplash color
android.presplash_color = #2196F3

# (str) Presplash animation
#android.presplash_animation =

# (str) Icon for the app
android.icon.filename = %(source.dir)s/../img/cover.jpg

# (str) Presplash image
android.presplash.filename = %(source.dir)s/../img/cover.jpg

# (bool) If True, then compile with release mode
android.release = True

# (str) Keystore for signing release APKs
android.sign.keystore = %(source.dir)s/xxtdocx.keystore

# (str) Keystore alias
android.sign.alias = xxtdocx

# (str) Keystore password
android.sign.keystore_password = xxtdocx2024

# (str) Keystore alias password
android.sign.alias_password = xxtdocx2024

# (list) List of permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Android features
#android.features =

# (bool) Use camera
#android.use_camera = False

# (list) Additional Java classes
#android.add_java_classes =

# (list) Java classes to override
#android.add_activities =

# (list) Services
#android.services =

# (list) Receivers
#android.receivers =

# (list) Intent filters
#android.intent_filters =

# (list) Meta data
#android.meta_data =

# (str) Extra Java code
#android.add_src =

# (str) compile SDK version
#android.compile_sdk =

# (str) Gradle dependencies
#android.gradle_dependencies =

# (str) AndroidX
#android.use_androidx = True

# (bool) Use Gradle
#android.use_gradle = True

# (str) Manifest file path
#android.manifest =

# (str) Application class
#android.application_class =

# (str) Service class
#android.service =

# (str) Activity class
#android.activity =

# (str) Theme
#android.theme =

# (str) Maven repositories
#android.maven_repositories =

# (list) Permissions presets
#android.permission_presets =

# (list) Feature presets
#android.feature_presets =

# (str) Gradle plugin
#android.gradle_plugin =

# (str) Gradle plugin version
#android.gradle_plugin_version =

# (str) Gradle version
#android.gradle_version =

# (str) Gradle build tools
#android.build_tools =

# (str) Extra env vars
#android.extra_env =

# (str) Extra Gradle args
#android.extra_gradle_args =

# (str) P4A extra args
#p4a.extra_args = --disable-recipes=pycryptodome


# (list) iOS/OSX frameworks
# ios.frameworks =

# (list) iOS/OSX plist
# ios.plist =

# (str) iOS/OSX entitlements
# ios.entitlements =

# (str) iOS/OSX main.cpp
# ios.main_cpp =

# (str) iOS/OSX bundle identifier
# ios.bundle_identifier = com.liuwanwan1.xxtdocx

# (str) iOS/OSX app name
# ios.app_name = 学习通作业提取

# (str) iOS/OSX version
# ios.version = 1.0.0

# (str) iOS/OSX team ID
# ios.team_id =

# (str) iOS/OSX code sign identity
# ios.codesign_identity =

# (str) iOS/OSX provision profile
# ios.provision_profile =

# (str) iOS/OSX icon
# ios.icon =

# (str) iOS/OSX launch image
# ios.launch_image =


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage
# build_dir = ./.buildozer

# (str) Path to build output
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    For example:
#      [app:meta_data]
#      my.meta = value1
#      other.meta = value2
#    -----------------------------------------------------------------------------
