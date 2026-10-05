Version bêta pour l'application PyCorrection. Ce logiciel permet d'automatiser la majorité des tâches de correction (e.g., gestion des fichiers en provenance de Moodle, gestion du fichier GeNote, vérification des références pour détecter l'usage de l'IA, etc).

Le logiciel a été testé sur Linux et Windows 10 dans une machine virtuelle et fonctionne comme prévu. Cependant, il est possible que certaines configurations sur différents ordinateurs provoquent des bugs mineurs (e.g., application qui ne se lance pas, features qui ne fonctionnent pas, etc). Le logiciel ne supprime aucun fichier, alors il n'y a pas de risques à ce niveau. 

Merci de bien vouloir me signaler tout problème pour m'aider à corriger les bugs et rendre l'application disponible 
au plus grand nombre d'utilisateurs possible! Les fichiers à télécharger sont dans la section Releases (dans la bar 
de navigation à droite, entre About et Packages)

### Instructions pour l'installation sur Windows

Vous devez télécharger le fichier Application-PyCorrection-Windows-x64.zip dans un répertoire qui ne nécessite pas de privilèges administrateurs (e.g., Documents). Vous pouvez ajouter un répertoire à l'intérieur de celui-ci pour mieux organiser les fichiers (e.g., Documents\Université). Le programme ne fonctionnera pas dans un répertoire comme C:/Program Files ou C:/Program Files (x86). 

Une fois le fichier décompressé, vous devriez avoir un répertoire Application-PyCorrection.  À l'intérieur de celui-ci se trouve l'application qui peut être lancée en cliquant sur l'icône PyCorrection-Windows-x64.exe. Vous pouvez ignorer l'avertissement de Windows defender. L'application n'est pas signée digitalement, car cela encourt des frais. Lorsque l'application va se lancer, un second répertoire nommé "data" va se créer à côté de l’icône PyCorrection-Windows-x64.exe. Il est bien important de ne pas modifier ou supprimer ce répertoire, car il contient la base de données et les préférences utilisateurs. 

Les fichiers de corrections et les fichiers GeNote seront gérés à partir du répertoire racine qui sera configuré dans la page configuration de l'application. Le répertoire Documents est configuré par défaut, mais vous pouvez le modifier pour n'importe quel répertoire qui ne nécessite pas de privilège administrateurs. 

Les instructions d'utilisation de l'application sont disponibles dans l'application à la page À propos et instructions. Vous pouvez télécharger le cours fictif dans le fichier "PyCorrection-Tutoriel.zip" pour suivre les instructions. 

### Instructions pour l'installation sur Linux

Vous devez télécharger le fichier Application-PyCorrection-Linux-x86_64.zip dans un répertoire qui ne nécessite pas de privilèges administrateurs (e.g., ~/Documents). Vous pouvez ajouter un répertoire à l'intérieur de celui-ci pour mieux organiser les fichiers (e.g., Documents/Université). Le programme ne fonctionnera pas dans un répertoire comme /opt.
 
Une fois le fichier décompressé, vous devriez avoir un répertoire Application-PyCorrection.  À l'intérieur de celui-ci se trouve l'application qui peut être lancée en cliquant sur l'icône PyCorrection-Linux-x86_64.AppImage.  Lorsque l'application va se lancer, un second répertoire nommé "data" va se créer à côté de l’icône  PyCorrection-Linux-x86_64.AppImage. Il est bien important de ne pas modifier ou supprimer ce répertoire, car il contient la base de données et les préférences utilisateurs. 

Les fichiers de corrections et les fichiers GeNote seront gérés à partir du répertoire racine qui sera configuré dans la page configuration de l'application. Le répertoire ~/Documents est configuré par défaut, mais vous pouvez le modifier pour n'importe quel répertoire qui ne nécessite pas de privilège administrateurs. 

Les instructions d'utilisation de l'application sont disponibles dans l'application à la page À propos et instructions. Vous pouvez télécharger le cours fictif dans le fichier "PyCorrection-Tutoriel.zip" pour suivre les instructions. 