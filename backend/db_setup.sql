-- Medication Box Recognition API — database schema + seed data
-- Run once on a fresh MySQL server:
--     mysql -u root -p < backend/db_setup.sql

CREATE DATABASE IF NOT EXISTS medicines_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medicines_db;

DROP TABLE IF EXISTS medicines;
CREATE TABLE `medicines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `dosage` varchar(50) DEFAULT NULL,
  `form` varchar(50) DEFAULT NULL,
  `form_ar` varchar(100) DEFAULT NULL,
  `usage_description` varchar(255) DEFAULT NULL,
  `name_ar` varchar(255) DEFAULT NULL,
  `usage_ar` text,
  `usage_fr` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (15, 'Augmentin', '100mg', 'sirop', 'شراب', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (22, 'Augmentin', '1g', 'comprimé', 'قرص', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (21, 'Augmentin', '1g', 'sachet', 'كيس', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (16, 'Augmentin', '312mg', 'sirop', 'شراب', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (17, 'Augmentin', '375mg', 'comprimé', 'قرص', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (18, 'Augmentin', '457mg', 'sirop', 'شراب', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (20, 'Augmentin', '500mg', 'sachet', 'كيس', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (19, 'Augmentin', '500mg', 'comprimé pelliculé', 'قرص مغلف', NULL, 'أوغمنتين', 'مضاد حيوي', 'Antibiotique');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (11, 'Brufen', '100mg', 'sirop', 'شراب', NULL, 'بروفين', 'مضاد للالتهابات', 'Anti-inflammatoire');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (12, 'Brufen', '100ml', 'sirop', 'شراب', NULL, 'بروفين', 'مضاد للالتهابات', 'Anti-inflammatoire');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (10, 'Brufen', '20mg', 'sirop', 'شراب', NULL, 'بروفين', 'مضاد للالتهابات', 'Anti-inflammatoire');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (13, 'Brufen', '400mg', 'comprimé pelliculé', 'قرص مغلف', NULL, 'بروفين', 'مضاد للالتهابات', 'Anti-inflammatoire');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (14, 'Brufen', '600mg', 'comprimé pelliculé', 'قرص مغلف', NULL, 'بروفين', 'مضاد للالتهابات', 'Anti-inflammatoire');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (2, 'Doliprane', '1000mg', 'gélule', 'كبسولة', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (3, 'Doliprane', '1000mg', 'comprimé effervescent', 'قرص فوار', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (4, 'Doliprane', '1000mg', 'sachet', 'كيس', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (1, 'Doliprane', '1000mg', 'comprimé', 'قرص', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (28, 'Doliprane', '100mg', 'suppositoire sécable', 'تحميلة قابلة للتقسيم', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fievre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (31, 'Doliprane', '100mg', 'sirop', 'شراب', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fievre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (29, 'Doliprane', '150mg', 'suppositoire', 'تحميلة', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fievre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (32, 'Doliprane', '150mg', 'sachet', 'كيس', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fievre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (30, 'Doliprane', '200mg', 'suppositoire', 'تحميلة', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fievre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (33, 'Doliprane', '200mg', 'sachet', 'كيس', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fievre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (9, 'Doliprane', '300mg', 'sachet', 'كيس', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (8, 'Doliprane', '500mg', 'gélule', 'كبسولة', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (7, 'Doliprane', '500mg', 'comprimé', 'قرص', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (6, 'Doliprane', '500mg', 'comprimé effervescent', 'قرص فوار', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (5, 'Doliprane', '500mg', 'sachet', 'كيس', NULL, 'دوليبران', 'تخفيف الألم والحمى', 'Soulagement de la douleur et de la fièvre');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (23, 'Smecta', '3g', 'sachet', 'كيس', NULL, 'سميكتا', 'علاج الجهاز الهضمي', 'Traitement digestif');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (25, 'Ventoline', '0.1mg', 'inhalateur', 'بخاخ للاستنشاق', NULL, 'فينتولين', 'علاج الربو', 'Traitement de l''asthme');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (26, 'Ventoline', '0.5mg', 'solution injectable', 'محلول للحقن', NULL, 'فينتولين', 'علاج الربو', 'Traitement de l''asthme');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (24, 'Ventoline', '100mcg', 'inhalateur', 'بخاخ للاستنشاق', NULL, 'فينتولين', 'علاج الربو', 'Traitement de l''asthme');
INSERT INTO medicines (`id`, `name`, `dosage`, `form`, `form_ar`, `usage_description`, `name_ar`, `usage_ar`, `usage_fr`) VALUES (27, 'Ventoline', '2mg', 'sirop', 'شراب', NULL, 'فينتولين', 'علاج الربو', 'Traitement de l''asthme');
