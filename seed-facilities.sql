-- US Cold facility data from uscold.com
-- Run this in Supabase SQL Editor
-- Matches on city+state; uses address as tiebreaker for multi-facility cities

-- Arlington TX
UPDATE facilities SET
  address='3300 E. Park Row Drive', zip='76010', phone='(817) 633-3070',
  pallet_positions=44768, temp_min_f=-10, temp_max_f=37,
  rail_access=true, rail_carrier='Union Pacific',
  repack=true, export_import=true
WHERE city='Arlington' AND state='TX';

-- Bakersfield CA
UPDATE facilities SET
  address='6501 District Blvd.', zip='93313', phone='(661) 832-2653',
  pallet_positions=44768, temp_min_f=-18, temp_max_f=34,
  rail_access=true, rail_carrier='Union Pacific',
  repack=true, export_import=true
WHERE city='Bakersfield' AND state='CA';

-- Bethlehem PA (Emery St)
UPDATE facilities SET
  address='15 Emery Street', zip='18015', phone='(610) 433-7378',
  pallet_positions=45491, temp_min_f=-5, temp_max_f=35,
  rail_access=true, rail_carrier='Phoenix Rail',
  repack=true, export_import=true
WHERE city='Bethlehem' AND state='PA' AND address ILIKE '%Emery%';

-- Bethlehem PA (Miller Circle)
UPDATE facilities SET
  address='4000 Miller Circle', zip='18020', phone='(610) 477-6820',
  pallet_positions=21235, temp_min_f=-10, temp_max_f=40,
  rail_access=true, rail_carrier='Union Pacific',
  repack=true, export_import=true
WHERE city='Bethlehem' AND state='PA' AND address ILIKE '%Miller%';

-- Covington TN
UPDATE facilities SET
  address='104 Witherington Drive', zip='38019', phone='(901) 313-2653',
  pallet_positions=48000, temp_min_f=-20, temp_max_f=32,
  automated=true, repack=true
WHERE city='Covington' AND state='TN';

-- Dallas South TX
UPDATE facilities SET
  address='2225 N. Cockrell Hill Road', zip='75212', phone='(214) 854-3100',
  pallet_positions=57031, temp_min_f=-5, temp_max_f=36,
  rail_access=true, rail_carrier='Union Pacific',
  quick_freeze=true, export_import=true
WHERE city='Dallas' AND state='TX' AND (address ILIKE '%Cockrell%' OR name ILIKE '%South%');

-- Dallas Halifax TX
UPDATE facilities SET
  address='3404 Halifax Street', zip='75247', phone='(214) 854-3100',
  pallet_positions=4436, temp_min_f=-5, temp_max_f=0
WHERE city='Dallas' AND state='TX' AND (address ILIKE '%Halifax%' OR name ILIKE '%Halifax%');

-- Denton TX (Jim Christal)
UPDATE facilities SET
  address='3255 Jim Christal Road', zip='76207', phone='(940) 295-7050',
  pallet_positions=29000, temp_min_f=-5, temp_max_f=34,
  rail_access=true, rail_carrier='BNSF',
  repack=true, export_import=true
WHERE city='Denton' AND state='TX' AND (address ILIKE '%Christal%' OR name NOT ILIKE '%Cold Creek%');

-- Denton Cold Creek TX
UPDATE facilities SET
  address='6651 N Interstate 35, Suite 161', zip='76207', phone='(940) 239-8950',
  pallet_positions=24916, temp_min_f=-20, temp_max_f=-5
WHERE city='Denton' AND state='TX' AND (address ILIKE '%Interstate%' OR name ILIKE '%Cold Creek%');

-- Fort Worth TX
UPDATE facilities SET
  address='2554 Downing Drive', zip='76106', phone='(817) 624-1900',
  pallet_positions=43000, temp_min_f=-5, temp_max_f=40,
  rail_access=true, rail_carrier='BNSF',
  automated=true, repack=true, export_import=true
WHERE city='Fort Worth' AND state='TX';

-- Fresno CA
UPDATE facilities SET
  address='2525 East North Avenue', zip='93725', phone='(559) 237-6145',
  pallet_positions=89000, temp_min_f=-20, temp_max_f=55,
  rail_access=true, rail_carrier='Union Pacific',
  quick_freeze=true, repack=true, export_import=true, organic=true
WHERE city='Fresno' AND state='CA';

-- Harrisonburg VA
UPDATE facilities SET
  address='780 Pleasant Valley Road', zip='22801', phone='(540) 564-6800',
  pallet_positions=18345, temp_min_f=0, temp_max_f=40,
  quick_freeze=true, export_import=true
WHERE city='Harrisonburg' AND state='VA';

-- Hazleton PA
UPDATE facilities SET
  address='1102 North Park Drive', zip='18202', phone='(570) 861-1000',
  pallet_positions=50434, temp_min_f=-20, temp_max_f=38,
  rail_access=true, rail_carrier='Norfolk Southern',
  repack=true, export_import=true
WHERE city='Hazleton' AND state='PA';

-- La Vergne TN
UPDATE facilities SET
  address='1727 J.P. Hennessy Drive', zip='37086', phone='(615) 641-9800',
  pallet_positions=23000, temp_min_f=-5, temp_max_f=38,
  rail_access=true, rail_carrier='CSX',
  quick_freeze=true, export_import=true
WHERE city='La Vergne' AND state='TN';

-- Lake City FL
UPDATE facilities SET
  address='211 NE McCloskey Avenue', zip='32055', phone='(386) 438-2653',
  pallet_positions=32000, temp_min_f=-20, temp_max_f=34,
  quick_freeze=true, repack=true, export_import=true
WHERE city='Lake City' AND state='FL';

-- Laredo I TX
UPDATE facilities SET
  address='18728 FM 1472 (Mines Road)', zip='78045', phone='(956) 267-2950',
  pallet_positions=24742, temp_min_f=-5, temp_max_f=38,
  repack=true, export_import=true, brcgs=true
WHERE city='Laredo' AND state='TX' AND (address ILIKE '%1472%' OR name ILIKE '%I%' OR pallet_positions=24742);

-- Laredo II TX
UPDATE facilities SET
  address='1601 Justo Penn Street', zip='78041', phone='(956) 722-8207',
  pallet_positions=10560, temp_min_f=-5, temp_max_f=40,
  rail_access=true, rail_carrier='Union Pacific',
  export_import=true, brcgs=true
WHERE city='Laredo' AND state='TX' AND (address ILIKE '%Penn%' OR pallet_positions=10560);

-- Laredo III TX
UPDATE facilities SET
  address='1602 Island St.', zip='78041', phone='(956) 722-3951',
  pallet_positions=31910, temp_min_f=-5, temp_max_f=65,
  rail_access=true, rail_carrier='Union Pacific',
  export_import=true
WHERE city='Laredo' AND state='TX' AND (address ILIKE '%Island%' OR pallet_positions=31910);

-- Lebanon IN
UPDATE facilities SET
  address='415 S. Mt. Zion Road', zip='46052', phone='(765) 482-2653',
  pallet_positions=41440, temp_min_f=-20, temp_max_f=65,
  automated=true, repack=true, export_import=true
WHERE city='Lebanon' AND state='IN';

-- Lumberton NC
UPDATE facilities SET
  address='2901 Kenny Biggs Road', zip='28358', phone='(910) 739-1992',
  pallet_positions=24778, temp_min_f=-10, temp_max_f=28,
  rail_access=true,
  quick_freeze=true, export_import=true, organic=true
WHERE city='Lumberton' AND state='NC';

-- McClellan CA
UPDATE facilities SET
  address='3936 Dudley Blvd.', city='McClellan', zip='95652', phone='(916) 640-2800',
  pallet_positions=83148, temp_min_f=-20, temp_max_f=50,
  rail_access=true,
  quick_freeze=true, automated=true, layer_pick=true,
  repack=true, export_import=true, organic=true
WHERE state='CA' AND (city ILIKE '%McClellan%' OR address ILIKE '%Dudley%');

-- McDonough 1 GA
UPDATE facilities SET
  address='1420 Greenwood Road', zip='30253', phone='(678) 554-2653',
  pallet_positions=27500, temp_min_f=-15,
  rail_access=true, rail_carrier='Norfolk Southern',
  automated=true, export_import=true, brcgs=true
WHERE city='McDonough' AND state='GA' AND (address ILIKE '%Greenwood%' OR pallet_positions=27500);

-- McDonough 2 GA
UPDATE facilities SET
  address='1275 Medline Place', zip='30253', phone='(678) 632-7450',
  pallet_positions=73027, temp_min_f=-5, temp_max_f=35,
  rail_access=true, rail_carrier='Norfolk Southern',
  automated=true, repack=true, export_import=true
WHERE city='McDonough' AND state='GA' AND (address ILIKE '%Medline%' OR pallet_positions=73027);

-- Milford DE
UPDATE facilities SET
  address='419 Milford-Harrington Highway, Route 14', zip='19963', phone='(302) 422-7536',
  pallet_positions=17582, temp_min_f=-10, temp_max_f=28,
  rail_access=true, rail_carrier='Norfolk Southern',
  quick_freeze=true, export_import=true
WHERE city='Milford' AND state='DE';

-- Minooka IL
UPDATE facilities SET
  address='601 Twin Rail Drive', zip='60447', phone='(815) 467-0455',
  pallet_positions=73000, temp_min_f=-20, temp_max_f=0,
  rail_access=true, rail_carrier='CSX',
  automated=true, layer_pick=true, repack=true, export_import=true, brcgs=true
WHERE city='Minooka' AND state='IL';

-- Hebron IN
UPDATE facilities SET
  address='17850 Colorado Street', zip='46341',
  pallet_positions=40000, temp_min_f=-20, temp_max_f=38,
  automated=true, layer_pick=true
WHERE city='Hebron' AND state='IN';

-- Omaha NE
UPDATE facilities SET
  address='4302 S. 30th Street', zip='68107', phone='(402) 731-9900',
  pallet_positions=16124, temp_min_f=-20, temp_max_f=45,
  rail_access=true, rail_carrier='Union Pacific / BNSF',
  quick_freeze=true, export_import=true
WHERE city='Omaha' AND state='NE';

-- Quakertown East PA
UPDATE facilities SET
  address='1050 Heller Road', zip='18951', phone='(215) 892-1541',
  pallet_positions=56248, temp_min_f=-20, temp_max_f=35,
  quick_freeze=true
WHERE city='Quakertown' AND state='PA' AND (address ILIKE '%Heller%' OR name ILIKE '%East%');

-- Quakertown West PA
UPDATE facilities SET
  address='4000 AM Drive', zip='18951', phone='(267) 875-6100',
  pallet_positions=25928, temp_min_f=-5, temp_max_f=36,
  quick_freeze=true
WHERE city='Quakertown' AND state='PA' AND (address ILIKE '%AM Drive%' OR name ILIKE '%West%');

-- Richmond / Prince George VA
UPDATE facilities SET
  address='8025 Quality Drive', city='Prince George', zip='23875', phone='(804) 451-7300',
  pallet_positions=5581, temp_min_f=-40, temp_max_f=0,
  export_import=true, dedicated=true
WHERE state='VA' AND (city ILIKE '%Richmond%' OR city ILIKE '%Prince George%' OR address ILIKE '%Quality%');

-- Smyrna TN
UPDATE facilities SET
  address='125 Threet Industrial Blvd.', zip='37167', phone='(615) 355-0047',
  pallet_positions=9300, temp_min_f=-5, temp_max_f=38,
  quick_freeze=true, automated=true, export_import=true
WHERE city='Smyrna' AND state='TN';

-- Syracuse UT
UPDATE facilities SET
  address='1093 West 450 South', zip='84075', phone='(801) 776-2653',
  pallet_positions=50000, temp_min_f=-20, temp_max_f=38,
  rail_access=true,
  automated=true, repack=true, export_import=true, brcgs=true
WHERE city='Syracuse' AND state='UT';

-- Tracy CA
UPDATE facilities SET
  address='1400 N. MacArthur Drive', zip='95376', phone='(209) 835-2653',
  pallet_positions=28000, temp_min_f=-20, temp_max_f=55,
  rail_access=true, rail_carrier='Union Pacific',
  quick_freeze=true, repack=true, export_import=true
WHERE city='Tracy' AND state='CA';

-- Tulare North CA
UPDATE facilities SET
  address='1021 E. Walnut Avenue', zip='93274', phone='(559) 686-1110',
  pallet_positions=87899,
  rail_access=true, rail_carrier='Union Pacific',
  repack=true, export_import=true
WHERE city='Tulare' AND state='CA' AND (address ILIKE '%Walnut%' OR name ILIKE '%North%');

-- Tulare South CA
UPDATE facilities SET
  address='810 E. Continental Avenue', zip='93274', phone='(559) 686-4996',
  pallet_positions=47496,
  rail_access=true, rail_carrier='Union Pacific',
  quick_freeze=true, repack=true, export_import=true
WHERE city='Tulare' AND state='CA' AND (address ILIKE '%Continental%' OR name ILIKE '%South%');

-- Turlock North CA
UPDATE facilities SET
  address='3500 W. Canal Drive, North Building', zip='95380', phone='(209) 668-1636',
  pallet_positions=40000, temp_min_f=34, temp_max_f=55,
  automated=true, repack=true, export_import=true, organic=true
WHERE city='Turlock' AND state='CA' AND (address ILIKE '%North%' OR name ILIKE '%North%');

-- Turlock South CA
UPDATE facilities SET
  address='3500 W. Canal Drive, South Building', zip='95380', phone='(209) 668-1636',
  pallet_positions=57000, temp_min_f=-10, temp_max_f=35,
  automated=true, repack=true, export_import=true, organic=true
WHERE city='Turlock' AND state='CA' AND (address ILIKE '%South%' OR name ILIKE '%South%');

-- Warsaw NC
UPDATE facilities SET
  address='240 Bruce Costin Road', zip='28398', phone='(910) 293-7400',
  pallet_positions=31000, temp_min_f=-20, temp_max_f=40,
  rail_access=true, rail_carrier='CSX',
  quick_freeze=true, automated=true, export_import=true
WHERE city='Warsaw' AND state='NC';

-- Wilmington IL
UPDATE facilities SET
  address='800 E. Kankakee River Drive', zip='60481', phone='(815) 476-2653',
  pallet_positions=51000, temp_min_f=-10, temp_max_f=36,
  automated=true, layer_pick=true, repack=true, export_import=true, brcgs=true
WHERE city='Wilmington' AND state='IL';
