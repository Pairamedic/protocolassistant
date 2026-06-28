#!/usr/bin/env python3
"""Generate fillable PDF checkoff forms for TruckCheck / EMS Check."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    HRFlowable, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus.flowables import Flowable
import os

# ── Output directory ──────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fillable_pdfs')
os.makedirs(OUT_DIR, exist_ok=True)

# ── Colors ────────────────────────────────────────────────────────────────────
DARK_NAVY  = colors.HexColor('#1e2230')
PURPLE     = colors.HexColor('#a855f7')
BLUE       = colors.HexColor('#3b82f6')
GREEN      = colors.HexColor('#22c55e')
LIGHT_GRAY = colors.HexColor('#f9fafb')
MID_GRAY   = colors.HexColor('#d1d5db')
TEXT_GRAY  = colors.HexColor('#6b7280')
RED_DARK   = colors.HexColor('#b91c1c')
WHITE      = colors.white
BLACK      = colors.black

# ── Styles ────────────────────────────────────────────────────────────────────
def ps(name, **kw):
    defaults = dict(fontName='Helvetica', fontSize=8, leading=10, textColor=BLACK)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

S = {
    'org':      ps('org',  fontName='Helvetica-Bold', fontSize=11, textColor=WHITE, leading=13),
    'sub':      ps('sub',  fontSize=7, textColor=colors.HexColor('#aaaaaa'), leading=9),
    'badge':    ps('badge',fontName='Helvetica-Bold', fontSize=8, textColor=WHITE,
                   leading=10, alignment=TA_CENTER),
    'sec':      ps('sec',  fontName='Helvetica-Bold', fontSize=6.5, textColor=WHITE,
                   leading=8, spaceAfter=0),
    'item':     ps('item', fontSize=7.5, leading=9),
    'qty':      ps('qty',  fontName='Helvetica-Bold', fontSize=7.5, leading=9,
                   textColor=colors.HexColor('#374151'), alignment=TA_CENTER),
    'chdr':     ps('chdr', fontSize=6, textColor=TEXT_GRAY, leading=7,
                   alignment=TA_CENTER),
    'chdr_l':   ps('chdr_l',fontSize=6, textColor=TEXT_GRAY, leading=7),
    'meta_lbl': ps('mlbl', fontSize=6, textColor=TEXT_GRAY, leading=7),
    'meta_val': ps('mval', fontName='Helvetica-Bold', fontSize=8, leading=10),
    'sig':      ps('sig',  fontSize=7, textColor=TEXT_GRAY, leading=8),
    'note':     ps('note', fontSize=6, textColor=TEXT_GRAY, leading=8),
    'note_b':   ps('noteb',fontName='Helvetica-Bold', fontSize=6,
                   textColor=RED_DARK, leading=8),
}

# ── Micro-flowables ───────────────────────────────────────────────────────────
class CheckBox(Flowable):
    def __init__(self, sz=7):
        super().__init__()
        self.sz = sz
        self.width = sz
        self.height = sz
    def draw(self):
        c = self.canv
        c.setStrokeColor(BLACK)
        c.setLineWidth(0.8)
        c.rect(0, 0, self.sz, self.sz, fill=0)

class Underline(Flowable):
    def __init__(self, w, h=10):
        super().__init__()
        self.width = w
        self.height = h
    def draw(self):
        c = self.canv
        c.setStrokeColor(BLACK)
        c.setLineWidth(0.5)
        c.line(0, 1.5, self.width, 1.5)

# ── Data ──────────────────────────────────────────────────────────────────────

ALS_PARA = [
  ('Soft Goods & Wound Care', [
    ('4×4 Pads',6,False),('ABD Pads',2,False),('Roller Gauze',6,False),
    ('Triangular Bandages',6,False),('Tape 1"',2,False),('Tape 2"',2,False),
    ('Commercial Tourniquet',1,False),('OB Kit',2,False),
  ]),
  ('Airway Supplies', [
    ('OPA Set (Adult / Child / Infant)',1,False),('NPA Set',1,False),
    ('Adult BVM (>1000mL)',2,False),('Pedi BVM (450-750mL)',1,False),
    ('Infant BVM (150-300mL)',1,False),('Magill Forceps - Adult',1,False),
    ('Magill Forceps - Pedi',1,False),('Nebulizer',2,False),
    ('Sterile Saline (for Nebulizer)',2,False),('CPAP',2,False),
  ]),
  ('Suction Supplies', [
    ('Portable Suction Unit',1,False),('On-Board Suction Unit',1,False),
    ('Suction Tubing',2,False),('Catheter 8fr / 10fr',1,False),
    ('Catheter 12fr',1,False),('Catheter 14fr / 18fr',1,False),
    ('Rigid Suction Tip',1,False),
  ]),
  ('Supraglottic / Adv. Airway', [
    ('Air-Q Size 0',1,False),('Air-Q Size 1',1,False),('Air-Q Size 1.5',1,False),
    ('Air-Q Size 2',1,False),('Air-Q Size 2.5',1,False),('Air-Q Size 3.5',1,False),
    ('Air-Q Size 4.5',1,False),('Tube Holder',1,False),
    ('Air-Q Stylet',2,False),('KY Jelly',3,False),
  ]),
  ('O2 Supplies', [
    ('Main O2 Cylinder',1,False),('O2 Regulator / Flowmeter',1,False),
    ('Nasal Cannula - Adult',4,False),('Nasal Cannula - Pedi',4,False),
    ('NRB Mask - Adult',4,False),('NRB Mask - Pedi',2,False),
    ('NRB Mask - Infant',2,False),
  ]),
  ('Portable O2', [
    ('Portable O2 Cylinder',1,False),('O2 Regulator',1,False),
    ('Nasal Cannula - Adult',2,False),('NRB Mask - Adult',2,False),
  ]),
  ('Cardiac Monitor', [
    ('Monitor Unit',1,False),('12-Lead Electrodes',1,False),
    ('Defib Pads - Adult',2,False),('Defib Pads - Pedi',1,False),
    ('SpO2 Probe - Adult',1,False),('SpO2 Probe - Pedi',1,False),
    ('ETCO2 Cable + Filterline',1,False),('NC EtCO2',1,False),
    ('4-Lead Cable',1,False),('12-Lead Cable',1,False),
    ('Electrodes - Adult (Packs)',20,False),('Electrodes - Pedi',5,False),
    ('EKG Paper Roll',1,False),('BP Cuff - Lg. Adult',1,False),
    ('BP Cuff - Adult',1,False),('BP Cuff - Child',1,False),
    ('BP Cuff - Infant',1,False),('BP Cuff - Thigh (Black)',1,False),
    ('Stethoscope',1,False),
  ]),
  ('Assessment & Monitoring', [
    ('Thermometer',1,False),('Glucometer',1,False),
    ('Glucometer Strips (Bottle)',1,True),('Lancets',20,False),
    ('Pen Light',1,False),
  ]),
  ('IV Supplies', [
    ('NS 1000mL',2,True),('LR 1000mL',4,True),('10gtt Set',4,False),
    ('Saline Lock',4,True),('Saline Flush',4,True),
    ('14G IV Cath',2,False),('16G IV Cath',2,False),
    ('18G IV Cath',4,False),('20G IV Cath',4,False),
    ('22G IV Cath',4,False),('24G IV Cath',2,False),
    ('Tourniquet',3,False),('Alcohol Preps',8,False),
    ('Non-Sterile 4x4',8,False),('1" Clear Tape',2,False),
  ]),
  ('IO Bag', [
    ('IO Drill (EZ-IO)',1,False),('IO Needle 15mm (Pink)',2,False),
    ('IO Needle 25mm (Blue)',2,False),('IO Needle 45mm (Yellow)',1,False),
    ('IO Stabilizer',2,False),('Extension Set',2,False),
    ('NS 1000mL (IO Flush)',1,True),('60mL Syringe',2,False),
  ]),
  ('BSI Supplies', [
    ('Exam Gloves (1 Box)',1,False),('Isolation Kits',2,False),
    ('N95 / N100 Respirator',1,False),('Eye Protection (Goggles)',2,False),
    ('Antiseptic Hand Cleaner',1,False),('Biohazard Bags',1,False),
  ]),
  ('Immobilization', [
    ('KED or Equivalent',1,False),('Spine Board + Straps',2,False),
    ('Pediatric Restraint System',1,False),('Head Immobilization Device',1,False),
    ('Cervical Collar - Adult',3,False),('Cervical Collar - Pediatric',2,False),
    ('Cervical Collar - Infant',1,False),
  ]),
  ('Splints & Transport', [
    ('Padded Extremity Splints (set)',1,False),('Traction Splint',1,False),
    ('Elevating Stretcher',1,False),('Stair Chair / Scoop Stretcher',1,False),
  ]),
  ('Trauma', [
    ('Trauma Dressing',4,False),('Occlusive Dressing',4,False),
    ('Vaseline Gauze',2,False),('Hemostatic Agent',1,False),
    ('Commercial Tourniquet (CAT)',2,False),('TXA',2,True),
  ]),
  ('Miscellaneous', [
    ('Fire Extinguisher',1,False),('HAZ-MAT Reference Guide',1,False),
    ('Reflective Safety Wear',1,False),('Flashlight + Batteries',1,False),
    ('Blankets',2,False),('Sheets',2,False),('Towels',2,False),
    ('Emesis Basin',1,False),('Sharps Container',1,False),
    ('EMT Shears',1,False),('Hemostat',1,False),('Lubricating Jelly',1,False),
    ('Window Punch',1,False),('Disinfectant Solution',1,False),
    ('Betadine Solution',1,False),('Pediatric Drug Reference',1,False),
    ('Sterile Water',1,False),('Car Seat or Pedi-Mate',1,False),
  ]),
  ('Medication Supplies', [
    ('18g Needles',8,False),('20g Needles',8,False),('21g Needles',4,False),
    ('20mL Syringe',2,False),('10mL Syringe',8,False),('3mL Syringe',6,False),
    ('1mL Syringe',1,False),('60mL Syringe',1,False),
    ('MAD Device (Mucosal Atomizer)',1,False),('Roll of Med Labels',1,False),
    ('Tape',4,False),
  ]),
  ('Medications', [
    ('Albuterol',6,True),('Atrovent',4,True),('Atropine',3,True),
    ('Epi 1:1',1,True),('Epi 1:10',2,True),('Lidocaine',2,True),
    ('Lidocaine Drip',1,True),('Dopamine Drip',2,True),('Narcan',4,True),
    ('Magnesium',1,True),('Calcium',1,True),('Hydralazine',2,True),
    ('Sodium Bicarb',2,True),('D10',3,True),('Lasix',2,True),
    ('Adenosine',3,True),('Zofran',4,True),('Labetalol',2,True),
    ('Thiamine',1,True),('Nitro',2,True),('Benadryl',2,True),
    ('Aspirin Bottle',1,True),('Verapamil',3,True),('Oral Glucose',1,True),
    ('Solu-Medrol',2,True),('Bacteriostatic Water',2,True),
    ('Amiodarone',2,True),('Glucagon',1,True),('Diltiazem',2,True),
  ]),
  ('Thomas Pack - IV Pouch 1', [
    ('NS 1000mL',1,True),('10gtt Set',1,False),('Tourniquet',1,False),
    ('Saline Lock',1,True),('Saline Flush',1,True),
    ('14G IV Cath',2,False),('16G IV Cath',2,False),
    ('18G IV Cath',3,False),('20G IV Cath',2,False),
    ('22G IV Cath',3,False),('24G IV Cath',3,False),
    ('Alcohol Preps',4,False),('Non-Sterile 4x4',4,False),
    ('1" Clear Tape',1,False),
  ]),
  ('Thomas Pack - IV Pouch 2', [
    ('NS 1000mL',1,True),('10gtt Set',1,False),('Tourniquet',1,False),
    ('Saline Lock',1,True),('Saline Flush',1,True),
    ('14G IV Cath',2,False),('16G IV Cath',2,False),
    ('18G IV Cath',2,False),('20G IV Cath',2,False),
    ('22G IV Cath',3,False),('24G IV Cath',3,False),
    ('Alcohol Preps',4,False),('Non-Sterile 4x4',4,False),
    ('1" Clear Tape',1,False),
  ]),
  ('Thomas Pack - Center Pouch', [
    ('Nitro',1,True),('Epi 1:10',1,True),('Atropine',1,True),
    ('D10 w/ 10gtt Set',1,True),('Amiodarone',1,True),
    ('Portable Sharps Container',1,False),
  ]),
  ('Thomas Pack - Top Outside Pocket', [
    ('Trauma Dressing',2,False),('Adult BP Cuff',1,False),('Stethoscope',1,False),
  ]),
  ('Thomas Pack - Inside Upper Pouch', [
    ('Adult BVM',1,False),('Adult Tube Turner',1,False),('10mL Syringe',1,False),
    ('Magill Forceps Adult',1,False),('Magill Forceps Pediatric',1,False),
    ('6.0 ETT',1,False),('7.0 ETT',1,False),('8.0 ETT',1,False),('9.0 ETT',1,False),
  ]),
  ('Thomas Pack - Right Outside Pocket', [
    ('Laryngoscope Handle',1,False),('Mac 2 Blade',1,False),
    ('Mac 3 Blade',1,False),('Mac 4 Blade',1,False),
    ('Miller 1 Blade',1,False),('Miller 2 Blade',1,False),
    ('Miller 3 Blade',1,False),('Miller 4 Blade',1,False),
  ]),
  ('Thomas Pack - Front Outside Pocket', [
    ('Non-Sterile 4x4',20,False),('2" Silk Tape',1,False),('ABD Pads',2,False),
    ('Vaseline Gauze',2,False),('Sheers',1,False),('Kling',4,False),
    ('Hemostats',1,False),('CAT Tourniquet',1,False),
  ]),
  ('Time Critical Dx Bands', [
    ('Trauma Bands',10,False),('Stroke Bands',10,False),
  ]),
]

BLS_EMT = [
  ('Soft Goods & Wound Care', [
    ('4x4 Pads',6,False),('ABD Pads',2,False),('Trauma Dressing',2,False),
    ('Roller Gauze',6,False),('Triangular Bandages',2,False),
    ('Isolation Kits',2,False),('Occlusive Dressing',2,False),
    ('Tape 1"',2,False),('Tape 2"',2,False),
    ('Commercial Tourniquet',1,False),('OB Kit',2,False),
  ]),
  ('Assessment & Monitoring', [
    ('Stethoscope',1,False),('BP Cuff - Lg. Adult',1,False),
    ('BP Cuff - Adult',1,False),('BP Cuff - Child',1,False),
    ('BP Cuff - Infant',1,False),('Pulse Oximeter',1,False),
    ('Pulse Ox Probe - Adult',1,False),('Pulse Ox Probe - Pedi',1,False),
    ('Thermometer',1,False),('Glucometer + Strips',1,False),
    ('Pen Light',1,False),('Pediatric Drug Reference',1,False),
  ]),
  ('AED', [
    ('AED Unit',1,False),('Adult Pads',2,False),('Pediatric Pads',2,False),
  ]),
  ('Airway', [
    ('OPA Set (Adult / Child / Infant)',1,False),('NPA Set',1,False),
    ('Nasal Cannula - Adult',4,False),('Nasal Cannula - Pedi',4,False),
    ('NRB Mask - Adult',4,False),('NRB Mask - Pedi',2,False),
    ('NRB Mask - Infant',2,False),('Adult BVM (>1000mL)',2,False),
    ('Pedi BVM (450-750mL)',1,False),('Infant BVM (150-300mL)',1,False),
    ('Magill Forceps - Adult',1,False),('Magill Forceps - Pedi',1,False),
  ]),
  ('Suction Supplies', [
    ('Portable Suction Unit',1,False),('On-Board Suction Unit',1,False),
    ('Suction Tubing',2,False),('Catheter 8fr / 10fr',1,False),
    ('Catheter 12fr',1,False),('Catheter 14fr / 18fr',1,False),
    ('Rigid Suction Tip',1,False),
  ]),
  ('Immobilization', [
    ('KED or Equivalent',1,False),('Spine Board + Straps',2,False),
    ('Pediatric Restraint System',1,False),('Head Immobilization Device',1,False),
    ('Cervical Collar - Adult',3,False),('Cervical Collar - Pediatric',2,False),
    ('Cervical Collar - Infant',1,False),
  ]),
  ('Splints & Transport', [
    ('Padded Extremity Splints (set)',1,False),('Traction Splint',1,False),
    ('Elevating Stretcher',1,False),('Stair Chair / Scoop Stretcher',1,False),
  ]),
  ('Miscellaneous', [
    ('Fire Extinguisher',1,False),('HAZ-MAT Reference Guide',1,False),
    ('Reflective Safety Wear',1,False),('Flashlight + Batteries',1,False),
    ('N95 / N100 Respirator',1,False),('Blankets',2,False),('Sheets',2,False),
    ('Towels',2,False),('Exam Gloves (1 Box)',1,False),
    ('Antiseptic Hand Cleaner',1,False),('Betadine Solution',1,False),
    ('Emesis Basin',1,False),('Sharps Container',1,False),
    ('EMT Shears',1,False),('Hemostat',1,False),('Lubricating Jelly',1,False),
    ('Window Punch',1,False),('Biohazard Bags',1,False),
    ('Disinfectant Solution',1,False),
  ]),
  ('EMT Medications', [
    ('Oral Glucose',1,True),('Activated Charcoal',1,True),
    ('Aspirin Bottle',1,True),('Albuterol (Unit Dose)',4,True),
    ('Epi Auto-Injector Adult',2,True),('Epi Auto-Injector Pedi',1,True),
    ('Naloxone (Narcan) Nasal',4,True),('MAD Device (Mucosal Atomizer)',1,False),
  ]),
]

ALS_AEMT = [
  ('Assessment & Monitoring', [
    ('Stethoscope',1,False),('BP Cuff - Lg. Adult',1,False),
    ('BP Cuff - Adult',1,False),('BP Cuff - Child',1,False),
    ('BP Cuff - Infant',1,False),('Pulse Oximeter',1,False),
    ('Pulse Ox Probe - Adult',1,False),('Pulse Ox Probe - Pedi',1,False),
    ('Thermometer',1,False),('Glucometer',1,False),
    ('Glucometer Strips (Bottle)',1,False),('Lancets',20,False),
    ('Pen Light',1,False),('Pediatric Drug Reference',1,False),
  ]),
  ('AED  (Required if No Cardiac Monitor)', [
    ('AED Unit',1,False),('Adult Pads',2,False),('Pediatric Pads',2,False),
  ]),
  ('Cardiac Monitor  (If Available)', [
    ('Electrodes - Adult (Packs)',20,False),('Electrodes - Pedi',5,False),
    ('EKG Paper Roll',1,False),('BP Cuff - Sm. Adult',1,False),
    ('BP Cuff - Adult (Navy)',1,False),('BP Cuff - Lg. Adult (Burgundy)',1,False),
    ('BP Cuff - Thigh (Black)',1,False),('Pedi Pulse Ox',2,False),
    ('ETT EtCO2',2,False),('NC EtCO2',1,False),('4-Lead Cable',1,False),
    ('12-Lead Cable (Acquire/Tx Only)',1,False),
  ]),
  ('BSI Supplies', [
    ('Exam Gloves (1 Box)',1,False),('Isolation Kits',2,False),
    ('N95/N100 Respirator',1,False),('Eye Protection (Goggles)',2,False),
    ('Antiseptic Hand Cleaner',1,False),
  ]),
  ('Soft Goods & Wound Care', [
    ('4x4 Pads',6,False),('Roller Gauze',6,False),('Tape 1"',2,False),
    ('Tape 2"',2,False),('Triangular Bandages',6,False),('OB Kit',2,False),
  ]),
  ('Trauma', [
    ('Trauma Dressing',4,False),('ABD Pads',12,False),('Sterile 4x4',10,False),
    ('Non-Sterile 4x4',40,False),('Occlusive Dressing',2,False),
    ('Vaseline Gauze',4,False),('Hemostatic Agent',1,False),('Kling',10,False),
    ('Silk Tape 2 inch',2,False),('Silk Tape 1 inch',2,False),
    ('Betadine (Bottle)',1,False),('Cold Pack',4,False),
    ('Box of Bandaids',1,False),('SAM Splints',2,False),
    ('Triangular Bandages',1,False),('CAT Tourniquet',1,False),
    ('Sterile Water',2,False),('Comm. Tourniquet (CAT)',2,False),
    ('TXA (Trauma)',2,True),
  ]),
  ('Airway', [
    ('OPA Set (Adult / Child / Infant)',1,False),('NPA Set',1,False),
    ('Nasal Cannula - Adult',8,False),('Nasal Cannula - Pedi',8,False),
    ('NRB Mask - Adult',4,False),('NRB Mask - Pedi',2,False),
    ('NRB Mask - Infant',2,False),('Adult BVM (>1000mL)',2,False),
    ('Pedi BVM (450-750mL)',1,False),('Infant BVM (150-300mL)',1,False),
    ('Magill Forceps - Adult',1,False),('Magill Forceps - Pedi',1,False),
    ('Nebulizer',1,False),('Sterile Saline (Neb.)',1,False),
    ('EtCO2 Nasal Cannula',2,False),('CPAP',2,False),
  ]),
  ('Suction Supplies', [
    ('Portable Suction Unit',1,False),('On-Board Suction Unit',1,False),
    ('Suction Tubing',2,False),('Catheter 8fr / 10fr',1,False),
    ('Catheter 12fr',1,False),('Catheter 14fr / 18fr',1,False),
    ('Rigid Suction Tip',1,False),
  ]),
  ('Supraglottic / Adv. Airway', [
    ('Air-Q Size 0',1,False),('Air-Q Size 0.5',1,False),('Air-Q Size 1.0',1,False),
    ('Air-Q Size 1.5',1,False),('Air-Q Size 2.0',1,False),
    ('Air-Q Size 2.5',1,False),('Air-Q Size 3.0',1,False),
    ('Air-Q Size 3.5',1,False),('Air-Q Size 4.0',1,False),
    ('Air-Q Size 4.5',1,False),('Air-Q Size 5 or Combitube',1,False),
    ('NPA - Assorted Sizes',1,False),('OPA - Assorted Sizes',1,False),
    ('ETT CO2 Detector',2,False),('Scalpel',1,False),('KY Jelly',3,False),
  ]),
  ('Immobilization', [
    ('KED or Equivalent',1,False),('Spine Board + Straps',2,False),
    ('Pedi Restraint System',1,False),('Head Immob. Device',1,False),
    ('Cervical Collar - Adult',3,False),('Cervical Collar - Pedi',2,False),
    ('Cervical Collar - Infant',1,False),
  ]),
  ('Splints & Transport', [
    ('Padded Extremity Splints',1,False),('Traction Splint',1,False),
    ('Elevating Stretcher',1,False),('Stair Chair / Scoop',1,False),
  ]),
  ('IO Bag', [
    ('IO Drill (EZ-IO)',1,False),('IO Needle 15mm (Pink)',2,False),
    ('IO Needle 25mm (Blue)',2,False),('IO Needle 45mm (Yellow)',1,False),
    ('IO Stabilizer',2,False),('Extension Set',2,False),
  ]),
  ('AEMT Medications', [
    ('Oral Glucose',1,True),('Aspirin Bottle',1,True),
    ('Albuterol (Unit Dose)',4,True),('Epi Auto-Injector Adult',2,True),
    ('Epi 1:10,000 (Injectable)',2,True),('Epi 1:1,000 (Injectable)',2,True),
    ('Naloxone (Narcan) Nasal',4,True),('MAD Device (Atomizer)',1,False),
    ('D10',2,True),('Atrovent',4,True),('Benadryl (Diphenhydramine)',2,True),
    ('Zofran (Ondansetron)',2,True),('Tylenol (Acetaminophen)',2,True),
    ('TXA (Tranexamic Acid)',2,True),
  ]),
  ('Medication Supplies', [
    ('18g Needles',8,False),('20g Needles',8,False),('21g Needles',4,False),
    ('20mL Syringe',2,False),('10mL Syringe',8,False),('3mL Syringe',6,False),
    ('1mL Syringe',1,False),('Roll of Med Labels',1,False),
    ('Med Labels / Tape',4,False),
  ]),
  ('IV Supplies', [
    ('NS 1000mL',2,True),('LR 1000mL',4,True),('Dial-a-Flow',2,False),
    ('10 gtts Set',4,False),('Saline Lock',4,True),('Saline Flush',4,True),
    ('14g Catheter (Angiocath)',2,False),('16g Catheter (Angiocath)',2,False),
    ('18g Catheter (Angiocath)',4,False),('20g Catheter (Angiocath)',4,False),
    ('22g Catheter (Angiocath)',4,False),('24g Catheter (Angiocath)',2,False),
    ('Alcohol Preps',8,False),('1" Clear Tape',2,False),
  ]),
  ('Miscellaneous', [
    ('Fire Extinguisher',1,False),('HAZ-MAT Reference Guide',1,False),
    ('Reflective Vests',3,False),('Flashlight + Batteries',1,False),
    ('Linens / Blankets / Towels',6,False),('Gloves - Small (box)',1,False),
    ('Gloves - Medium (box)',1,False),('Gloves - Large (box)',1,False),
    ('Gloves - XL (box)',1,False),('Emesis Basin',1,False),
    ('Sharps Container',1,False),('EMT Shears',1,False),('Hemostat',1,False),
    ('Lubricating Jelly',1,False),('Window Punch',1,False),
    ('Disinfectant Spray / Wipes',1,False),('Thermometer w/ Covers',1,False),
    ('Biohazard Bags',5,False),('Heater or Ice Chest (Seasonal)',1,False),
    ('Heating Pad (Seasonal)',1,False),('START Triage Bag',1,False),
    ('Mega Mover',2,False),('Car Seat or Pedi-Mate',1,False),
  ]),
]

UCO = [
  ('Fluids & Engine', [
    'Fuel Level','Oil Level','Radiator Water Level','P/S Fluid Level',
    'Windshield Fluid Level','Trans Fluid Level','Belts / Hose / Wires',
  ]),
  ('Cab & Controls', [
    'Vehicle Horn','Batteries - Left','Batteries - Right','Wipers',
    'Windshield','Front Dome Light','Driver and Passenger Seatbelt',
    'High Idle','Brakes','Test Emergency Brake','Bottle of Cleaner',
  ]),
  ('Communications', [
    'F-3 Radio (EASI NET)','F-2 (High Band)','Hospital Radio',
    'Sirens','Portable Radio','iPad / Tablet',
  ]),
  ('Emergency Lighting', ['Light Bar','Wig Wags','Strobes']),
  ('Exterior Lights', [
    'Head Lights - Low Beam','Head Lights - High Beam','Tail Lights',
    'Back Up Lights','Scene Lights - Left','Scene Lights - Right',
    'Scene Lights - Rear','Turn Signal - Left','Turn Signal - Right',
    'Parking Lights','Clearance Lights','Air Horn',
  ]),
  ('Patient Compartment', [
    'Patient Compartment Lights','Patient Compartment Seatbelts / Stretcher',
  ]),
  ('Tire Inspection', ['Pressure','Wear and Cuts','Rims / Simulators']),
]

# ── Section table builder ─────────────────────────────────────────────────────

def equip_section_table(title, items, cw):
    """One unified table: dark header row + item rows. Fits in a Table cell."""
    has_exp = any(exp for _,_,exp in items)

    # proportional widths that sum to cw (no leading checkbox column)
    min_w = 22
    act_w = 28
    exp_w = 26 if has_exp else 0
    oos_w = 20
    lbl_w = cw - min_w - act_w - exp_w - oos_w

    widths = [lbl_w, min_w, act_w]
    if has_exp:
        widths.append(exp_w)
    widths.append(oos_w)

    # Column header row
    hdr = [Paragraph('Item', S['chdr_l']), Paragraph('Min', S['chdr']),
           Paragraph('Actual', S['chdr'])]
    if has_exp:
        hdr.append(Paragraph('Exp', S['chdr']))
    hdr.append(Paragraph('OOS', S['chdr']))

    # Title row spans all cols
    n_cols = len(widths)
    title_row = [Paragraph(title.upper(), S['sec'])] + ['' for _ in range(n_cols - 1)]

    rows = [title_row, hdr]
    ts_cmds = [
        # Title row
        ('BACKGROUND',    (0, 0), (-1, 0), DARK_NAVY),
        ('SPAN',          (0, 0), (-1, 0)),
        ('LEFTPADDING',   (0, 0), (-1, 0), 5),
        ('TOPPADDING',    (0, 0), (-1, 0), 2),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        # Col header row
        ('BACKGROUND',    (0, 1), (-1, 1), LIGHT_GRAY),
        ('LINEBELOW',     (0, 1), (-1, 1), 0.3, MID_GRAY),
        ('TOPPADDING',    (0, 1), (-1, 1), 1),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 1),
        # All rows
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 2),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
        ('TOPPADDING',    (0, 2), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 2), (-1, -1), 2),
        ('ALIGN',         (1, 0), (1, -1), 'CENTER'),
        ('ALIGN',         (-1, 0), (-1, -1), 'CENTER'),
        ('BOX',           (0, 0), (-1, -1), 0.5, MID_GRAY),
    ]

    for i, (label, qty, exp) in enumerate(items):
        row_i = i + 2  # offset for title+header rows
        row = [Paragraph(label, S['item']),
               Paragraph(f'x{qty}', S['qty']), Underline(act_w - 6)]
        if has_exp:
            row.append(Underline(exp_w - 6) if exp else '')
        row.append(CheckBox(7))
        rows.append(row)
        if i % 2 == 1:
            ts_cmds.append(('BACKGROUND', (0, row_i), (-1, row_i), LIGHT_GRAY))
        ts_cmds.append(('LINEBELOW', (0, row_i), (-1, row_i), 0.3, colors.HexColor('#f0f0f0')))

    t = Table(rows, colWidths=widths, repeatRows=0)
    t.setStyle(TableStyle(ts_cmds))
    return t


def uco_section_table(title, items, cw):
    cb_w  = 12
    lbl_w = cw - cb_w
    n_cols = 2

    title_row = [Paragraph(title.upper(), S['sec']), '']
    rows = [title_row]
    ts_cmds = [
        ('BACKGROUND',    (0, 0), (-1, 0), DARK_NAVY),
        ('SPAN',          (0, 0), (-1, 0)),
        ('LEFTPADDING',   (0, 0), (-1, 0), 5),
        ('TOPPADDING',    (0, 0), (-1, 0), 2),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 1), (-1, -1), 3),
        ('RIGHTPADDING',  (0, 1), (-1, -1), 3),
        ('TOPPADDING',    (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ('BOX',           (0, 0), (-1, -1), 0.5, MID_GRAY),
    ]
    for i, item in enumerate(items):
        row_i = i + 1
        rows.append([CheckBox(8), Paragraph(item, S['item'])])
        if i % 2 == 1:
            ts_cmds.append(('BACKGROUND', (0, row_i), (-1, row_i), LIGHT_GRAY))
        ts_cmds.append(('LINEBELOW', (0, row_i), (-1, row_i), 0.3, colors.HexColor('#f0f0f0')))

    t = Table(rows, colWidths=[cb_w, lbl_w])
    t.setStyle(TableStyle(ts_cmds))
    return t

# ── Header ────────────────────────────────────────────────────────────────────

def build_header(form_title, badge_label, badge_color, meta_fields, W):
    n = len(meta_fields)
    mw = W / n

    # Top bar
    top = Table(
        [[Paragraph('Emergency Ambulance Service, Inc.', S['org']),
          Paragraph(badge_label, S['badge'])]],
        colWidths=[W * 0.76, W * 0.24],
    )
    top.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), DARK_NAVY),
        ('BACKGROUND',    (1, 0), (1, 0), badge_color),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (0, 0), 7),
        ('RIGHTPADDING',  (1, 0), (1, 0), 7),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    # Subtitle strip
    sub_text = 'Unit Check-Off' if 'Unit Check' in badge_label else 'Ambulance Equipment Check-Off'
    sub = Table(
        [[Paragraph(sub_text, S['sub'])]],
        colWidths=[W],
    )
    sub.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor('#2d3347')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 7),
        ('TOPPADDING',    (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    # Meta fields row
    meta_cells = []
    for label, _ in meta_fields:
        meta_cells.append([
            Paragraph(label, S['meta_lbl']),
            Underline(mw - 14),
        ])
    meta_row = Table([meta_cells], colWidths=[mw] * n)
    meta_row.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEAFTER',     (0, 0), (-2, -1), 0.4, MID_GRAY),
        ('BACKGROUND',    (0, 0), (-1, -1), WHITE),
    ]))

    wrapper = Table([[top], [sub], [meta_row]], colWidths=[W])
    wrapper.setStyle(TableStyle([
        ('BOX',           (0, 0), (-1, -1), 1.2, DARK_NAVY),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return wrapper

# ── UCO closing ───────────────────────────────────────────────────────────────

def build_uco_closing(W):
    repairs = Table([
        [Paragraph('REPAIRS NEEDED / NEW BODY DAMAGE', S['sec'])],
        [Underline(W - 14)],
        [Underline(W - 14)],
    ], colWidths=[W])
    repairs.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), DARK_NAVY),
        ('BOX',           (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
    ]))

    fc_w  = W * 0.20
    ext_w = W * 0.45
    mn_w  = W * 0.35

    def yn_cell(label, cell_w):
        inner = Table(
            [[CheckBox(7), Paragraph('YES', S['item']),
              CheckBox(7), Paragraph('NO', S['item'])]],
            colWidths=[10, 24, 10, 20],
        )
        inner.setStyle(TableStyle([
            ('VALIGN',        (0,0),(-1,-1),'MIDDLE'),
            ('LEFTPADDING',   (0,0),(-1,-1),1),
            ('RIGHTPADDING',  (0,0),(-1,-1),1),
            ('TOPPADDING',    (0,0),(-1,-1),0),
            ('BOTTOMPADDING', (0,0),(-1,-1),0),
        ]))
        return [Paragraph(label, S['meta_lbl']), inner]

    bottom = Table([[
        yn_cell('Fuel Card', fc_w),
        [Paragraph('Fire Extinguisher PSI / Status', S['meta_lbl']),
         Underline(ext_w - 16)],
        yn_cell('Maint. Request Turned In', mn_w),
    ]], colWidths=[fc_w, ext_w, mn_w])
    bottom.setStyle(TableStyle([
        ('BOX',           (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('LINEAFTER',     (0, 0), (1, 0), 0.4, MID_GRAY),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    return [repairs, Spacer(1, 4), bottom]

# ── Signature block ───────────────────────────────────────────────────────────

def build_sigs(sigs, W):
    n  = len(sigs)
    cw = W / n
    cells = [[Underline(cw - 16), Paragraph(s, S['sig'])] for s in sigs]
    t = Table([cells], colWidths=[cw] * n)
    t.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'BOTTOM'),
        ('TOPPADDING',    (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
    ]))
    return t

# ── Main builder ──────────────────────────────────────────────────────────────

def build_pdf(fname, form_title, badge_label, badge_color,
              meta_fields, sections, sigs, is_uco=False):
    path = os.path.join(OUT_DIR, fname)
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=0.45*inch, rightMargin=0.45*inch,
        topMargin=0.40*inch, bottomMargin=0.40*inch,
    )
    W = letter[0] - 0.90*inch
    col_w = (W - 6) / 2

    story = []
    story.append(build_header(form_title, badge_label, badge_color, meta_fields, W))
    story.append(Spacer(1, 5))

    if is_uco:
        sec_tables = [uco_section_table(t, items, col_w) for t, items in sections]
    else:
        sec_tables = [equip_section_table(t, items, col_w) for t, items in sections]

    # Two-column grid: pair up section tables
    gap = Spacer(6, 1)
    pairs = []
    for i in range(0, len(sec_tables), 2):
        L = sec_tables[i]
        R = sec_tables[i+1] if i+1 < len(sec_tables) else ''
        pairs.append([L, R])

    grid = Table(pairs, colWidths=[col_w, col_w], hAlign='LEFT',
                 spaceBefore=0, spaceAfter=0)
    grid.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',   (0,0), (-1,-1), 0),
        ('RIGHTPADDING',  (0,0), (-1,-1), 0),
        ('TOPPADDING',    (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        # gap between columns
        ('RIGHTPADDING',  (0,0), (0,-1), 3),
        ('LEFTPADDING',   (1,0), (1,-1), 3),
    ]))
    story.append(grid)

    if is_uco:
        story.append(Spacer(1, 5))
        story.extend(build_uco_closing(W))

    if not is_uco:
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            '<b>OOS</b> = Out of Stock — check the OOS box if the item is unavailable.',
            S['note']
        ))

    story.append(build_sigs(sigs, W))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width=W, thickness=0.3, color=MID_GRAY))
    story.append(Paragraph('EMS Check  ·  Emergency Ambulance Service, Inc.', S['note']))

    doc.build(story)
    print(f'  OK: {path}')

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('Generating fillable PDFs ...')

    build_pdf(
        'ALS_Paramedic_Equipment_Checkoff.pdf',
        'Ambulance Equipment Check-Off', 'ALS - Paramedic', PURPLE,
        [('Unit #',''),('Date',''),('Paramedic',''),('EMT',''),
         ('Main O2 (PSI)',''),('Portable O2 (PSI)',''),('Narcotic Seal #','')],
        ALS_PARA,
        ['Paramedic Signature', 'EMT Signature'],
    )

    build_pdf(
        'ALS_AEMT_Equipment_Checkoff.pdf',
        'Ambulance Equipment Check-Off', 'ALS - AEMT', BLUE,
        [('Unit #',''),('Date',''),('AEMT',''),('EMT',''),
         ('Main O2 (PSI)',''),('Portable O2 (PSI)','')],
        ALS_AEMT,
        ['AEMT Signature', 'EMT Signature'],
    )

    build_pdf(
        'BLS_EMT_Equipment_Checkoff.pdf',
        'Ambulance Equipment Check-Off', 'BLS - EMT', GREEN,
        [('Unit #',''),('Date',''),('EMT 1',''),('EMT 2',''),
         ('Main O2 (PSI)',''),('Portable O2 (PSI)','')],
        BLS_EMT,
        ['EMT 1 Signature', 'EMT 2 Signature'],
    )

    build_pdf(
        'Unit_Checkoff.pdf',
        'Unit Check-Off', 'Unit Check', BLUE,
        [('Unit #',''),('Date',''),('Mileage',''),('EMT',''),('Radio #','')],
        UCO,
        ['EMT Signature', 'Supervisor'],
        is_uco=True,
    )

    print('Done.')
