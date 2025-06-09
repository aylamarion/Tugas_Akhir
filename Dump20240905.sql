-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: heartcheckdb
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `heartcheck`
--

-- DROP TABLE IF EXISTS `heartcheck`; -- COBA DIHAPUS
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
-- USE jantung;
CREATE TABLE `heartcheck` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int DEFAULT NULL,
  `checkResult` varchar(24) DEFAULT NULL,
  `video_path` varchar(255) DEFAULT NULL,
  `checked_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `heartcheck_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patientdata` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci; -- COLLATE=utf8mb4_0900_ai_ci
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `heartcheck`
--

LOCK TABLES `heartcheck` WRITE;
/*!40000 ALTER TABLE `heartcheck` DISABLE KEYS */;
INSERT INTO `heartcheck` VALUES (20,1,'Normal','https://heartcheckbucket.s3.amazonaws.com/user1_data/John Doe_data/2024-07-01/result_068f2f02.mp4','2024-07-01 03:40:46'),(21,1,'Tidak Normal','https://heartcheckbucket.s3.amazonaws.com/user1_data/John Doe_data/2024-07-01/result_2f5c7121.mp4','2024-07-01 03:41:55'),(22,1,'Normal','https://heartcheckbucket.s3.amazonaws.com/user1_data/John Doe_data/2024-07-01/result_d0948e6a.mp4','2024-07-01 03:46:25'),(23,1,'Normal','https://heartcheckbucket.s3.amazonaws.com/user1_data/John Doe_data/2024-07-10/result_105521d6.mp4','2024-07-10 13:17:22'),(24,1,'Tidak Normal','https://heartcheckbucket.s3.amazonaws.com/user1_data/John Doe_data/2024-07-10/result_203d88d6.mp4','2024-07-10 13:17:48'),(25,1,'Tidak Normal','https://heartcheckbucket.s3.amazonaws.com/user1_data/John Doe_data/2024-07-10/result_39a6eae1.mp4','2024-07-10 14:15:46'),(26,1,'Normal','https://heartcheckbucket.s3.amazonaws.com/user1_data/John Doe_data/2024-07-10/result_457ccf79.mp4','2024-07-10 14:16:06');
/*!40000 ALTER TABLE `heartcheck` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patientdata`
--

-- DROP TABLE IF EXISTS `patientdata`; -- COBA DIHAPUS
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patientdata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `patient_name` varchar(128) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `patientdata_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci; -- COLLATE=utf8mb4_0900_ai_ci
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patientdata`
--

LOCK TABLES `patientdata` WRITE;
/*!40000 ALTER TABLE `patientdata` DISABLE KEYS */;
INSERT INTO `patientdata` VALUES (1,1,'John Doe',10,'2014-06-03',0),(2,1,'Jane Doe',19,'2005-06-10',1),(3,1,'Jovan Josafat',21,'2003-01-09',0),(4,1,'Febriola Sinambela',10,'2014-05-01',1);
/*!40000 ALTER TABLE `patientdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

-- DROP TABLE IF EXISTS `role`; -- COBA DIHAPUS
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `permissions` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci; -- COLLATE=utf8mb4_0900_ai_ci
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'user','user are doctors','write, read, edit, delete');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles_users`
--

-- DROP TABLE IF EXISTS `roles_users`; -- COBA DIHAPUS
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `roles_users_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `roles_users_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci; -- COLLATE=utf8mb4_0900_ai_ci
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles_users`
--

LOCK TABLES `roles_users` WRITE;
/*!40000 ALTER TABLE `roles_users` DISABLE KEYS */;
INSERT INTO `roles_users` VALUES (1,1,1);
/*!40000 ALTER TABLE `roles_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

-- DROP TABLE IF EXISTS `user`; -- COBA DIHAPUS
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `current_login_at` datetime DEFAULT NULL,
  `last_login_ip` varchar(100) DEFAULT NULL,
  `current_login_ip` varchar(100) DEFAULT NULL,
  `login_count` int DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `fs_uniquifier` varchar(64) NOT NULL,
  `confirmed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fs_uniquifier` (`fs_uniquifier`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci; -- COLLATE=utf8mb4_0900_ai_ci
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'user1@user.com','user1','$2b$12$iMtsFx5PDekZbNrgMGOHaeOkJtJhBnZh4JLC1CYRYU1XKq0yANoHa',NULL,NULL,NULL,NULL,NULL,1,'3d6f71b53101457db0aa31575c04380b',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-05 19:04:50
