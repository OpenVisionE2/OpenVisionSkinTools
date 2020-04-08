from distutils.core import setup
import setup_translate

pkg = 'Extensions.OpenVisionSkinTools'
setup (name = 'enigma2-plugin-extensions-openvisionskintools',
       version = '1.0',
       description = 'Plugin to skin style.',
       packages = [pkg],
       package_dir = {pkg: 'usr'},
       package_data = {pkg: ['plugin.png', '*/*.png', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass = setup_translate.cmdclass, # for translation
      )
