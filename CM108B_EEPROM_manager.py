import configparser
import argparse
import os.path
import hid
import time

# initialize parser
parser = argparse.ArgumentParser(epilog="RC1")

# script arguments
parser.add_argument("-bc","--burn_config", help="Generate and burn EEPROM data from config file.")
parser.add_argument("-s","--save", help="Save generated binary file.")
parser.add_argument("-bb","--burn_bin", help="Burn a binary file to EEPROM.")
parser.add_argument("-r","--read", help="Read and dump EEPROM to a binary file.")
parser.add_argument("-e","--erase", action='store_true', help="Erase device EEPROM.")
parser.add_argument("-v","--vid", help="Target device VID. Defaults to 0x0D8C.")
parser.add_argument("-p","--pid", help="Target device PID. Defaults to 0x0012.")
parser.add_argument("-l","--list", action='store_true', help="List all CM108B devices.")

args = parser.parse_args()

CM108_USB = hid.device()

EEPROM_content = []
EEPROM_max_adress = 0x3F
content_max_adress = 0X32

WRITE_COMMAND = 0XC0
WRITE_CYCLE_WAIT = 0.010 #10 ms on CM108B datasheet
READ_COMMAND = 0X80

def twos_complement(value, bits):
    if value < 0:
        value = value % (1 << bits)
    return value

def bytes_to_word16(high, low):
    return low + (high << 8)

def hex_from_cfg(cfgfile):
    print("Reading configuration...")

    config = configparser.ConfigParser()
    config.read(cfgfile)

    serial_control = int(config['Device']['serial_number_enable_control'])
    audio_value_valid = int(config['Device']['audio_config_values_valid'])
    serial_number = config['Device']['serial_number']

    vid = int(config['Device']['VID'], 16)
    pid = int(config['Device']['PID'], 16)

    product_string = config['Device']['product_string']
    manufacturer_string = config['Device']['manufacturer_string']

    DAC_initial_volume = int(config['Audio_Config']['DAC_initial_volume'])
    DAC_min_max_volume_valid = int(config['Audio_Config']['DAC_min_max_volume_valid'])
    DAC_min_volume = int(config['Audio_Config']['DAC_min_volume'])
    DAC_max_volume = int(config['Audio_Config']['DAC_max_volume'])

    ADC_initial_volume = int(config['Audio_Config']['ADC_initial_volume'])
    ADC_min_max_volume_valid = int(config['Audio_Config']['ADC_min_max_volume_valid'])
    ADC_min_volume = int(config['Audio_Config']['ADC_min_volume'])
    ADC_max_volume = int(config['Audio_Config']['ADC_max_volume'])

    AA_initial_volume = int(config['Audio_Config']['AA_initial_volume'])
    AA_min_max_volume_valid = int(config['Audio_Config']['AA_min_max_volume_valid'])
    AA_min_volume = int(config['Audio_Config']['AA_min_volume'])
    AA_max_volume = int(config['Audio_Config']['AA_max_volume'])

    boost_mode = int(config['Audio_Config']['boost_mode'])
    DAC_shutdown = int(config['Audio_Config']['DAC_shutdown'])
    total_power_control = int(config['Audio_Config']['total_power_control'])

    MIC_high_pass_filter = int(config['Audio_Config']['MIC_high_pass_filter'])
    MIC_PLL_adjust = int(config['Audio_Config']['MIC_PLL_adjust'])
    MIC_boost = int(config['Audio_Config']['MIC_boost'])

    DAC_output_terminal = int(config['Audio_Config']['DAC_output_terminal'])
    hid_enable = int(config['Audio_Config']['hid_enable'])

    remote_wakeup = int(config['Audio_Config']['remote_wakeup'])

    i2s_output_disable = int(config['Audio_Config']['i2s_output_disable'])

    print("Generating hex file...")
    print("Generating device config...")

    #calcul 0x00
    word_value = 0x6700 + 0b101 + (serial_control << 1) + (audio_value_valid << 3)
    EEPROM_content.append(word_value)
    print("0x00: "+f"{word_value:#0{6}x}")

    #VID & PID (0x01 & 0x02)
    EEPROM_content.append(vid)
    print("0x01: "+f"{vid:#0{6}x}")

    EEPROM_content.append(pid)
    print("0x02: "+f"{pid:#0{6}x}")

    #serial number (0x03 to 0x09)
    serial_number_size = len(serial_number)

    if serial_number_size > 13:
        print("Serial number is too long ! (max 13 characters)")
        print("Limiting to 13 characters.")
        serial_number_size = 13
    
    #constructing serial number chunk bytes
    serial_number_bytes = []
    serial_number_bytes.append((serial_number_size+1)*2)

    for index in range(13):
        if index >= serial_number_size:
            serial_number_bytes.append(0x00)
        else:
            serial_number_bytes.append(int.from_bytes(serial_number[index].encode('latin-1')))

    for index in range(7):
        word_value = bytes_to_word16(serial_number_bytes[2*index + 1], serial_number_bytes[2*index])
        EEPROM_content.append(word_value)
        ad = index + 3
        print(f"{(ad):#0{4}x} : "+f"{word_value:#0{6}x}")

    #product string (0x0A to 0x19)
    product_string_size = len(product_string)

    if product_string_size > 31:
        print("Product name is too long ! (max 31 characters)")
        print("Limiting to 31 characters.")
        product_string_size = 31
    
    #constructing product number chunk bytes
    product_bytes = []
    product_bytes.append((product_string_size+1)*2)

    for index in range(31):
        if index >= product_string_size:
            product_bytes.append(0x00)
        else:
            product_bytes.append(int.from_bytes(product_string[index].encode('latin-1')))

    for index in range(16):
        word_value = bytes_to_word16(product_bytes[2*index + 1], product_bytes[2*index])
        EEPROM_content.append(word_value)
        ad = index + 0xA
        print(f"{(ad):#0{4}x} : "+f"{word_value:#0{6}x}")

    #manufacturer string (0x1A to 0x29)
    manufacturer_string_size = len(manufacturer_string)

    if manufacturer_string_size > 31:
        print("Manufacturer name is too long ! (max 31 characters)")
        print("Limiting to 31 characters.")
        manufacturer_string_size = 31
    
    #constructing product number chunk bytes
    manufacturer_bytes = []
    manufacturer_bytes.append((manufacturer_string_size+1)*2)

    for index in range(31):
        if index >= manufacturer_string_size:
            manufacturer_bytes.append(0x00)
        else:
            manufacturer_bytes.append(int.from_bytes(manufacturer_string[index].encode('latin-1')))

    for index in range(16):
        word_value = bytes_to_word16(manufacturer_bytes[2*index + 1], manufacturer_bytes[2*index])
        EEPROM_content.append(word_value)
        ad = index + 0x1A
        print(f"{(ad):#0{4}x} : "+f"{word_value:#0{6}x}")
    
    print("Generating audio config...")

    #audio options (0x2A to 0x31) - note: volumes are 2's complement

    if (audio_value_valid):
        word_value = AA_min_max_volume_valid + (ADC_min_max_volume_valid << 1) + (DAC_min_max_volume_valid << 2) + (twos_complement(ADC_initial_volume, 6) << 3) + (twos_complement(DAC_initial_volume, 7) << 9)
    else:
        word_value = 0x0000

    EEPROM_content.append(word_value)
    print("0x2A: "+f"{word_value:#0{6}x}")

    if (audio_value_valid):
        word_value = remote_wakeup + (hid_enable << 1) + (DAC_output_terminal << 2) + (MIC_boost << 3) + (MIC_PLL_adjust << 4) + (MIC_high_pass_filter << 5) + (total_power_control << 7) + (DAC_shutdown << 8) + (boost_mode << 9) + (twos_complement(AA_initial_volume, 5) << 11)
    else:
        word_value = 0x0000

    EEPROM_content.append(word_value)
    print("0x2B: "+f"{word_value:#0{6}x}")

    if (audio_value_valid and DAC_min_max_volume_valid):
        word_value = twos_complement(DAC_min_volume, 8) << 8
    else:
        word_value = 0x0000
    
    EEPROM_content.append(word_value)
    print("0x2C: "+f"{word_value:#0{6}x}")

    if (audio_value_valid and DAC_min_max_volume_valid):
        word_value = twos_complement(DAC_max_volume, 8) << 8
    else:
        word_value = 0x0000

    EEPROM_content.append(word_value)
    print("0x2D: "+f"{word_value:#0{6}x}")

    if (audio_value_valid and ADC_min_max_volume_valid):
        word_value = twos_complement(ADC_min_volume, 8) << 8
    else:
        word_value = 0x0000

    EEPROM_content.append(word_value)
    print("0x2E: "+f"{word_value:#0{6}x}")

    if (audio_value_valid and ADC_min_max_volume_valid):
        word_value = twos_complement(ADC_max_volume, 8) << 8
    else:
        word_value = 0x0000

    EEPROM_content.append(word_value)
    print("0x2F: "+f"{word_value:#0{6}x}")

    if (audio_value_valid and AA_min_max_volume_valid):
        word_value = twos_complement(AA_min_volume, 8) << 8
    else:
        word_value = 0x0000

    EEPROM_content.append(word_value)
    print("0x30: "+f"{word_value:#0{6}x}")

    if (audio_value_valid and AA_min_max_volume_valid):
        word_value = twos_complement(AA_max_volume, 8) << 8
    else:
        word_value = 0x0000

    EEPROM_content.append(word_value)
    print("0x31: "+f"{word_value:#0{6}x}")

    #EE_OPTION2 register (0x32)
    word_value = i2s_output_disable << 1
    EEPROM_content.append(word_value)
    print("0x32: "+f"{word_value:#0{6}x}")

    print("hex file generated.")

    if args.save is not None:
        with open(args.save, "wb") as file:
            for data in EEPROM_content:
                data_low = data&0xFF
                data_high = (data >> 8) & 0xFF
                file.write(data_low.to_bytes())
                file.write(data_high.to_bytes())
        print("hex file saved to "+args.save+".")
    
    burn_eeprom(EEPROM_content)

def open_device():
    if args.vid is not None and args.pid is not None:
        CM108_USB.open(int(args.vid, 16), int(args.pid, 16))
    else:
        print("No device argument. Using first CM108B device.")
        CM108_USB.open(0x0D8C, 0x0012)

def write_16(command, adress, data=0xFFFF):
    array = []
    array.append(0x00) #report ID
    array.append(0x80) #EEPROM access
    array.append(data & 0xFF) #data low octet
    array.append((data >> 8) & 0xFF) #data high octet
    array.append(command | adress) #EEPROM_control
    CM108_USB.write(array)
    time.sleep(WRITE_CYCLE_WAIT)

def read_16():
    array = CM108_USB.read(4)
    return array[1] + (array[2] << 8)

def burn_eeprom(data):
    open_device()
    print("Burning EEPROM !")
    for ad in range(content_max_adress + 1):
        write_16(WRITE_COMMAND, ad, data[ad])
        print(f"{ad:#0{4}x}"+": "+f"{data[ad]:#0{6}x}")

    print("EEPROM burned.")
    print("Please disconnect and reconnect the device for the computer to take the modification into account!")

def read_eeprom():
    open_device()

    print("Reading EEPROM !")

    for ad in range(content_max_adress + 1):
        write_16(READ_COMMAND, ad)

        data = read_16()
        EEPROM_content.append(data&0xFF)
        EEPROM_content.append((data >> 8) & 0xFF)
        print(f"{ad:#0{4}x}"+": "+f"{data:#0{6}x}")
        
    print("EEPROM read.")

    with open(args.read, "wb") as file:
        for data in EEPROM_content:
            file.write(data.to_bytes())

    print("Data dumped in "+args.read)

def erase_eeprom():
    open_device()

    print("Erasing EEPROM !")

    for ad in range(EEPROM_max_adress + 1):
        write_16(WRITE_COMMAND, ad)

    print("Erasure done !")
    print("Please disconnect and reconnect the device for the computer to take the modification into account!")

def list_devices():
    for device in hid.enumerate(0x0D8C, 0x0012):
        print(device.get('product_string') + "/" + device.get('manufacturer_string') + "(SN#" + device.get('serial_number') + ") path=" + device['path'].decode('utf-8') if isinstance(device['path'], bytes) else device['path']) 

if args.burn_config is not None:
    hex_from_cfg(args.burn_config)
elif args.burn_hex is not None:
    if os.path.getsize(args.burn_hex) == 102:
        with open(args.burn_hex, "rb") as file:
            while (data := file.read(1)):
                EEPROM_content.append(int.from_bytes(data))
        burn_eeprom(EEPROM_content)
    else:
        print("Wrong hex file size ! It must be 102 octets.")
elif args.read:
    read_eeprom()
elif args.erase:
    erase_eeprom()
elif args.list:
    list_devices()
else:
    parser.print_help()