#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup
import setup_translate

pkg = 'Extensions.OpenVisionSkinTools'
setup (name='enigma2-plugin-extensions-openvisionskintools',
       version='1.0',
       description='Tool for changing skin styles',
       packages=[pkg],
       package_dir={pkg: 'plugin'},
       package_data={pkg: ['plugin.png', '*/*.png', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass=setup_translate.cmdclass, # for translation
      )
