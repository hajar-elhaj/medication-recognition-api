-- Run this once to add the medicine form column.
-- Possible values: 'tablet', 'sachet', 'syrup', 'capsule', 'spray', 'drops'

ALTER TABLE medicines
    ADD COLUMN form VARCHAR(50) NULL AFTER dosage;

-- Then fill in the values for your existing rows (examples):
UPDATE medicines SET form = 'tablet'  WHERE name = 'Doliprane' AND dosage IN ('300mg','500mg','1000mg');
UPDATE medicines SET form = 'tablet'  WHERE name = 'Brufen'    AND dosage IN ('200mg','400mg','600mg');
UPDATE medicines SET form = 'syrup'   WHERE name = 'Brufen'    AND dosage = '100ml';
UPDATE medicines SET form = 'sachet'  WHERE name = 'Smecta'    AND dosage = '3g';
UPDATE medicines SET form = 'tablet'  WHERE name = 'Augmentin' AND dosage IN ('500mg','1g');
UPDATE medicines SET form = 'sachet'  WHERE name = 'Augmentin' AND dosage IN ('312mg','357mg','457mg');
UPDATE medicines SET form = 'syrup'   WHERE name = 'Augmentin' AND dosage = '100mg';
UPDATE medicines SET form = 'inhaler' WHERE name = 'Ventoline';
