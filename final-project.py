import os
import subprocess
import argparse
import csv

import matplotlib.pyplot as plt

CSR_ADDR = 0x0
COEF_ADDR = 0x4
OUTCAP_ADDR = 0x8


class Csr():
    def __init__(self, csr_bin):
        self.fen = (csr_bin >> 0) & 0x1
        self.c0en = (csr_bin >> 1) & 0x1
        self.c1en = (csr_bin >> 2) & 0x1
        self.c2en = (csr_bin >> 3) & 0x1
        self.c3en = (csr_bin >> 4) & 0x1
        self.halt = (csr_bin >> 5) & 0x1
        self.sts = (csr_bin >> 6) & 0x3
        self.ibcnt = (csr_bin >> 8) & 0xff
        self.ibovf = (csr_bin >> 16) & 0x1
        self.ibclr = (csr_bin >> 17) & 0x1
        self.tclr = (csr_bin >> 18) & 0x1
        self.rnd = (csr_bin >> 19) & 0x3
        self.icoef = (csr_bin >> 21) & 0x1
        self.icap = (csr_bin >> 22) & 0x1
        self.rsvd = (csr_bin >> 23) & 0xffff

    def encode(self):
        return (
            ((self.fen & 0x1) << 0) |
            ((self.c0en & 0x1) << 1) |
            ((self.c1en & 0x1) << 2) |
            ((self.c2en & 0x1) << 3) |
            ((self.c3en & 0x1) << 4) |
            ((self.halt & 0x1) << 5) |
            ((self.sts & 0x3) << 6) |
            ((self.ibcnt & 0xff) << 8) |
            ((self.ibovf & 0x1) << 16) |
            ((self.ibclr & 0x1) << 17) |
            ((self.tclr & 0x1) << 18) |
            ((self.rnd & 0x3) << 19) |
            ((self.icoef & 0x1) << 21) |
            ((self.icap & 0x1) << 22) |
            ((self.rsvd & 0x3ff) << 23)
        )
    

    def __str__(self):
        str_rep = "CSR Register Content\n"
        str_rep += f"fen   : {hex(self.fen)}\n"
        str_rep += f"c0en  : {hex(self.c0en)}\n"
        str_rep += f"c1en  : {hex(self.c1en)}\n"
        str_rep += f"c2en  : {hex(self.c2en)}\n"
        str_rep += f"c3en  : {hex(self.c3en)}\n"
        str_rep += f"halt  : {hex(self.halt)}\n"
        str_rep += f"sts   : {hex(self.sts)}\n"
        str_rep += f"ibcnt : {hex(self.ibcnt)}\n"
        str_rep += f"ibovf : {hex(self.ibovf)}\n"
        str_rep += f"ibclr : {hex(self.ibclr)}\n"
        str_rep += f"tclr  : {hex(self.tclr)}\n"
        str_rep += f"rnd   : {hex(self.rnd)}\n"
        str_rep += f"icoef : {hex(self.icoef)}\n"
        str_rep += f"icap  : {hex(self.icap)}\n"
        str_rep += f"rsvd  : {hex(self.rsvd)}"
        return str_rep

class Coef():
    def __init__(self, coef_bin):
        self.c0 = (coef_bin >> 0) & 0xff
        self.c1 = (coef_bin >> 8) & 0xff
        self.c2 = (coef_bin >> 16) & 0xff
        self.c3 = (coef_bin >> 24) & 0xff

    def encode(self):
        return (
            ((self.c0 & 0xff) << 0) |
            ((self.c1 & 0xff) << 8) |
            ((self.c2 & 0xff) << 16) |
            ((self.c3 & 0xff) << 24)
        )
    
    def __str__(self):
        str_rep = "COEF Register Content\n"
        str_rep += f"c0 : {hex(self.c0)}\n"
        str_rep += f"c1 : {hex(self.c1)}\n"
        str_rep += f"c2 : {hex(self.c2)}\n"
        str_rep += f"c3 : {hex(self.c3)}"
        return str_rep

class Outcap():
    def __init__(self, outcap_bin):
        self.hcap = (outcap_bin >> 0) & 0xff
        self.lcap = (outcap_bin >> 8) & 0xff
        self.rsvd = (outcap_bin >> 16) & 0xffff

    def encode(self):
        return (
            ((self.hcap & 0xff) << 0) |
            ((self.lcap & 0xff) << 8) |
            ((self.rsvd & 0xff) << 16)
        )
    
    def __str__(self):
        str_rep = "OUTCAP Register Content\n"
        str_rep += f"hcap : {hex(self.hcap)}\n"
        str_rep += f"lcap : {hex(self.lcap)}\n"
        str_rep += f"rsvd : {hex(self.rsvd)}"
        return str_rep

class Uad():
  def __init__(self, inst_name=None):
    self.inst = inst_name
    self.csr = None
    self.coef = None
    self.outcap = None


  FEN   = 1 << 0  # bit 0
  HALT  = 1 << 5  # bit 5
  IBCNT = 0xff00  # bit 15 to 8
  IBOVF = 1 << 16 # bit 16
  IBCLR = 1 << 17 # bit 17

  def reset(self):
    return os.system(f'{self.inst} com --action reset')

  def disable(self):
    return os.system(f'{self.inst} com --action disable')

  def enable(self):
    return os.system(f'{self.inst} com --action enable')

  def read_CSR(self):
    csr_bytes = subprocess.check_output(f'{self.inst} cfg --address {CSR_ADDR}')
    return int(csr_bytes, 0)
 
  def read_COEF(self):
    csr_bytes = subprocess.check_output(f'{self.inst} cfg --address {COEF_ADDR}')
    return int(csr_bytes, 0)

  def read_OUTCAP(self):
    csr_bytes = subprocess.check_output(f'{self.inst} cfg --address {OUTCAP_ADDR}')
    return int(csr_bytes, 0)
  
  def write_CSR(self, data):
    csr_bytes = subprocess.check_output(f'{self.inst} cfg --address {CSR_ADDR} --data {hex(data)}')
    return int(csr_bytes, 0)
  
  def _set_bits(self, mask):
    return self.write_CSR(self.read_CSR() | mask)

  def _clear_bits(self, mask):
    return self.write_CSR(self.read_CSR() & ~mask)

  def _get_bits(self, mask): 
    csr = self.read_CSR()
    lsb = (mask & -mask).bit_length() - 1
    return (csr & mask) >> lsb

  def halt(self):
    return self._set_bits(self.HALT)

  def resume(self):
    return self._clear_bits(self.HALT)
  
  def filter_enable(self):
    return self._set_bits(self.FEN)
  
  def filter_disable(self):
    return self._clear_bits(self.FEN)
  
  def enter_bypass_mode(self):
    self.halt()
    self.filter_disable()
    self.resume()

  def exit_bypass_mode(self):
    self.halt()
    self.filter_enable()
    self.resume()

  def write_signal_channel(self, data):    
    out_bytes = subprocess.check_output(f'{self.inst} sig --data {hex(data)}')
    if out_bytes:
      return int(out_bytes, 0)
    else:
      return None
    
  def get_buffer_count(self):
    return self._get_bits(self.IBCNT)
  
  def get_buffer_overflow(self):
    return self._get_bits(self.IBOVF)
    
  def clear_buffer(self):
    return self._set_bits(self.IBCLR)

  def get_csr(self): 
    csr_bin = subprocess.check_output(f'{self.inst} cfg --address {CSR_ADDR}').decode()
    csr_bin = int(csr_bin, 0)
    self.csr = Csr(csr_bin)
    return self.csr

  def get_coef(self): 
    coef_bin = subprocess.check_output(f'{self.inst} cfg --address {COEF_ADDR}').decode()
    coef_bin = int(coef_bin, 0)
    self.coef = Coef(coef_bin)
    return self.coef

  def get_outcap(self): 
    outcap_bin = subprocess.check_output(f'{self.inst} cfg --address {OUTCAP_ADDR}').decode()
    outcap_bin = int(outcap_bin, 0)
    self.outcap = Outcap(outcap_bin)
    return self.outcap

  def set_csr(self, csr):
    exit_code = os.system(f'{self.inst} cfg --address {CSR_ADDR} --data {hex(self.csr.encode())}')
    self.get_csr()
    return exit_code

  def set_coef(self, coef):
    exit_code = os.system(f'{self.inst} cfg --address {COEF_ADDR} --data {hex(self.coef.encode())}')
    self.get_coef()
    return exit_code

  def set_outcap(self):
    exit_code = os.system(f'{self.inst} cfg --address {OUTCAP_ADDR} --data {hex(self.outcap.encode())}')
    self.get_outcap()   
    return exit_code

  def get_reg(self, reg_name): 
    if reg_name == 'csr':
        return self.get_csr()

    elif reg_name == 'coef':
        return self.get_coef()

    elif reg_name == 'outcap':
        return self.get_outcap()
    
  def set_reg(self, reg_name):
    if reg_name == 'csr':
        return self.set_csr()

    elif reg_name == 'coef':
        return self.set_coef()

    elif reg_name == 'outcap':
        return self.set_outcap()

def twos_comp(x):
    return ((x & 0x7F) - (x & 0x80)) / 64

def test_config(uad, cfg_file):
  uad.reset()
  uad.enable()
  
  # Set filter config
  uad.halt()
  with open(cfg_file, 'r') as f:
    csr = uad.get_csr()
    coef = uad.get_coef()
    for row in csv.DictReader(f):
        setattr(csr, f'c{row["coef"]}en', int(row['en'], 0))
        setattr(coef, f'c{row["coef"]}', int(row['value'], 0))
    uad.set_csr(csr)
    uad.set_coef(coef)
  uad.resume()

def run_process(uad, vec_file):
  uad.enable()
  uad.resume()
  uad.exit_bypass_mode()
  uad.clear_buffer()

  sig_out = []
  with open(vec_file, 'r') as f:
    for line in f:
      samp_in = int(line, 0)
      samp_out = uad.write_signal_channel(samp_in)
      sig_out.append(twos_comp(samp_out))

  return sig_out

def test_global_enable(uad):
  print("Resetting and enabling IP..")
  uad.reset()
  uad.enable()
  uad.disable()
  try:
    print("Reading CSR..")
    csr_hex = hex(uad.read_CSR())
    print(f"CSR value: {csr_hex}")
  except subprocess.CalledProcessError as e:
    return "PASSED: Outcome is expected"
  else:
    return "FAILED: Register is readable when disabled"


def test_por(uad, por_file):
    print("Resetting and enabling IP..")
    uad.reset()
    uad.enable()
    
    csr = uad.get_csr()
    coef = uad.get_coef()
    outcap = uad.get_outcap()

    passed = True

    with open(por_file, 'r') as f:
        for row in csv.DictReader(f):
            reg = None
            if row['register'] == 'csr':
                reg = csr

            elif row['register'] == 'coef':
                reg = coef

            elif row['register'] == 'outcap':
                reg = outcap

            actual_value = getattr(reg, row['field'])
            expected_value = int(row['value'], 0)
            if actual_value != expected_value:
                print(f'field {row["register"]}.{row["field"]} does not match. expected: {hex(expected_value)}, got {hex(actual_value)}')
                passed = False

    if passed: 
        return "PASSED: POR register matches reference file"
    return "FAILED: POR register does not match reference file"

def test_bypass(uad):
  # Reset DUT and bring it to a known enabled, non-bypass state
  uad.reset()
  uad.enable()
  # --- Enter bypass mode ---
  print("Entering Bypass mode..")
  uad.enter_bypass_mode()
  sig_in_array = [0xa3, 0xa3, 0xf0, 0xf0, 0x1d]
  sig_out_array = []
  for sig_in in sig_in_array:
    sig_out = uad.write_signal_channel(sig_in)
    print(f"Input signal: {hex(sig_in)}  Output signal: {hex(sig_out)}")
    sig_out_array.append(sig_out)
  # Restore normal operation
  uad.exit_bypass_mode()
  # In bypass mode, input should propagate directly to output
  if sig_in_array == sig_out_array:
    return "PASSED: Output signal matches input signal"
  else:
    return "FAILED: Output signal is different from input signal"


def test_buffer(uad):
  # Reset and enable device
  uad.reset()
  uad.enable()

  # Halt the filter to stop processing
  uad.halt()
  uad.filter_enable()  # filter still enabled, just halted
  print("Filter halted. Initial buffer count:", uad.get_buffer_count())

  # Start writing to input buffer
  print("\nWriting values to buffer...")
  for i in range(5):  # example: write 10 values
      uad.write_signal_channel(0x1)
      print(f"After write {i+1}, buffer count:", uad.get_buffer_count())
      
  if uad.get_buffer_count() != 5:
    return "FAILED: Buffer count error"

  # Write enough to cause overflow (more than 255)
  print("\nWriting to cause overflow...")
  total_writes = 260
  for i in range(1, total_writes + 1):
      uad.write_signal_channel(0x1)
      if i % 50 == 0 or i == total_writes:
          count = uad.get_buffer_count()
          overflow = uad.get_buffer_overflow()
          print(f"After write {i}: buffer count = {count}, overflow = {overflow}")

  if not uad.get_buffer_overflow():
    return "FAILED: Overflow flag error"

  # Clear buffer
  uad.clear_buffer()
  print("\nBuffer cleared. Current buffer count:", uad.get_buffer_count(), ". Overflow flag:", uad.get_buffer_overflow())

  if uad.get_buffer_count() != 0:
    return "FAILED: Buffer clear error"

  # Unhalt filter
  uad.resume()
  return "PASSED input buffer test"

def test_process(uad, vec_file, plot=False):
    csr = uad.get_csr()
    csr.fen = 1
    csr.tclr = 1
    csr.ibclr = 1
    uad.set_csr(csr)

    sig_in, sig_out = [], []
    with open(vec_file) as f:
        for l in f:
            sig_in.append(int(l, 0))

    for s in sig_in:
        sig_out.append(uad.write_signal_channel(s))

    if plot:
        plt.plot([twos_comp(x) for x in sig_in], label="Input", drawstyle="steps-post")
        plt.plot([twos_comp(x) for x in sig_out], label="Output", drawstyle="steps-post")
        plt.legend()
        plt.title("Signal Input vs Output")
        plt.show()

    print("PASS: Signal processing executed")
    return sig_out

def test_processall(golden_uad, dut_uad, vec_file):
  cfg_files = ["p0.cfg","p4.cfg","p7.cfg","p9.cfg"]

  if not cfg_files:
    print("No .cfg files found")
    return

  print(f"Found {len(cfg_files)} config files\n")

  for cfg in cfg_files:
    cfg_name = os.path.basename(cfg)
    print(f"=== Testing {cfg_name} ===")

    # --- Program golden ---
    test_config(golden_uad, cfg)
    golden_out = run_process(golden_uad, vec_file)

    # --- Program DUT ---
    test_config(dut_uad, cfg)
    dut_out = run_process(dut_uad, vec_file)

    # --- Compare ---
    mismatches = []
    for i, (g, d) in enumerate(zip(golden_out, dut_out)):
      if g != d:
        mismatches.append((i, g, d))

    if not mismatches:
        print("PASSED")
    else:
      print(f"FAILED: ({len(mismatches)} mismatches)")
      for i, g, d in mismatches[:5]:  # limit spam
        print(f"  sample {i}: golden={g}, dut={d}")
      if len(mismatches) > 5:
        print("  ...")

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--instance', help='instance to test')
  parser.add_argument('-t', '--test', choices=['dump', 'set', 'global_en', 'por', 'bypass', 'buffer', 'config', 'drive', 'process', 'processall'], help='the tests that can be run with this script')
  parser.add_argument('-v', '--value', help='register field value to set')
  parser.add_argument('-f', '--file', help='path to csv file with the expected por register values')
  parser.add_argument('-p', '--plot', action='store_true')
  args = parser.parse_args()

  uad = Uad(args.instance)
  print(f"\n= Testing {uad.inst} =")

  if args.test == 'global_en':
    test_global_enable(uad)

  if args.test == 'por':
    test_por (uad, args.file)

  if args.test == 'buffer':
    print(test_buffer(uad))

  if args.test == 'bypass':
    print(test_bypass(uad))

  if args.test == 'process':
    print(test_process(uad, args.file, args.plot))

  if args.test == 'processall':
    if args.file is None:
        print("Expected vector file, argument -f")
    else:
        golden = Uad("golden")
        test_processall(golden, uad, args.file)


if __name__ == "__main__":
  main()