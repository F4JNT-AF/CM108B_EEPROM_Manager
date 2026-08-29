# CM108B EEPROM Manager
## [EN] (FR below)
A Python script to easily program the EEPROM of CM108B devices ([such as my ham radio interface](https://github.com/F4JNT-AF/CM108_Radio_Interface)) and set device name, serial number and audio options.

:warning: **Do not modify VID, PID and HID if you don't know what you're doing. EEPROM will be hard to rewrite.** :warning: 

It can be used to:
* Read and dump the EEPROM contents in a file.
* Write configuration to the EEPROM, using either a:
	* A configuration file from which the program will generate EEPROM content. (default example given in config.ini)
	* A file containing raw EEPROM content ("binary" or "bin").
* Wipe the EEPROM.

### Required
hidapi library for Python (https://github.com/trezor/cython-hidapi/)
Note: Even if I use Windows, this should work on Linux and MacOS.

### Erase EEPROM
	python CM108B_EEPROM_manager.py --erase

### Burn config file to EEPROM
	python CM108B_EEPROM_manager.py --burn_config config.ini

### Burn binary file to EEPROM
	python CM108B_EEPROM_manager.py --burn_bin contents.bin

### Read and dump EEPROM content to binary file
	python CM108B_EEPROM_manager.py --read contents.bin

:information_source: Windows may not take into account the changes, even if you unplug and reconnect the device. A reboot is advised.

:information_source: The CM108B documentation is, on a lot of points, conflicting at best and not telling anything at worst and there was a lot of trial and error involved. The .ini file is documented with all known parameters. Other hidden options may lurk in the EE_OPTION2 register.


## [FR]
Un programme Python afin de facilement programmer l'EEPROM d'une carte CM108B ([telle que mon interface radio-PC](https://github.com/F4JNT-AF/CM108_Radio_Interface)) et personnaliser son nom, son numéro de série et ses options audio.

:warning: **Ne pas modifier le VID, PID ou HID si vous ne savez pas ce que vous faites. Il sera difficile de reprogrammer l'EEPROM.** :warning: 

Ce programme peut être utilisé pour:
* Lire et enregistrer le contenu de l'EEPROM dans un fichier.
* Écrire une configuration dans l'EEPROM, à partir d'un:
	* Fichier de configuration à partir duquel le programme générera le contenu brut de l'EEPROM. (config.ini donne un exemple)
	* Fichier contenu brut ("binaire") de l'EEPROM.
* Effacer l'EEPROM.

### Requis
La bibliothéque hidapi pour Python (https://github.com/trezor/cython-hidapi/)
Note: Même si j'utilise Windows, cela devrait marcher sur Linux et MacOS.

### Effacer l'EEPROM
	python .\CM108B_EEPROM_manager.py --erase

### Écrire un fichier de config dans l'EEPROM
	python CM108B_EEPROM_manager.py --burn_config config.ini

### Écrire un fichier binaire dans l'EEPROM
	python CM108B_EEPROM_manager.py --burn_bin contents.bin

### Lire et enregistrer le contenu de l'EEPROM dans un fichier binaire
	python CM108B_EEPROM_manager.py --read contents.bin

:information_source: Windows risque de ne pas prendre en compte les changements, même en déconnectant et reconnectant la carte. Il est conseillé de redémarrer.

:information_source: La documentation du CM108B est au mieux contradictoire, au pire complètement silencieuse sur beaucoup de sujets, inutile de dire qu'il y a eu pas mal de tatonnements et d'essais. Le fichier.ini documente toutes le paramètres connue (+1 caché). D'autres options cachées peuvent encore trainer dans le registre EE_OPTION2.
