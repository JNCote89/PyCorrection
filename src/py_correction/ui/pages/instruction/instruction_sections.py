from typing import override

from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.collapsible_sections import DefaultCollapsibleSection
from src.py_correction.ui.feedbacks.styles.base_style import HREF_STYLE
from src.py_correction.ui.pages.instruction.instruction_widget import FAQBlockText, InstructionBlockText, \
    OptionsBlockText


class AboutCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._collapsible_section = DefaultCollapsibleSection(title="À propos")
        self._collapsible_section.content_group_box.setProperty("class", "instruction_collapsible_section")

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._features_overview = FAQBlockText(
            block_question="Quelles sont les fonctionnalités principales de l'application?",
            block_answer=f"""L'application vise principalement à automatiser la gestion des cours à partir d'une 
            feuille GeNote, mais il est possible de l'utiliser en entrant manuellement les informations pertinentes.
            Les principales fonctions sont : 
            <ul>
            <li style='line-height:1.5;'>
            Création automatique des répertoires pertinents pour classer les fichiers relatifs à la correction
            (remises étudiantes, corrections, notes et gabarits de correction);
            </li>
            <li style='line-height:1.5;'>
            Configuration des gabarits de correction Excel pour extraire les notes de l'ensemble des étudiants 
            automatiquement;
            </li>
            <li style='line-height:1.5;'>
            Gestion des étudiants actifs et inactifs;
            </li>
            <li style='line-height:1.5;'>
            Extraction et classification automatiques des fichiers .zip en provenance de Moodle dans des répertoires
            spécifiques à chaque évaluation pour les travaux remis par les étudiants; 
            </li>
            <li style='line-height:1.5;'>
            Génération des grilles individuelles de correction au nom de chaque étudiant et classification de celles-ci
            dans des répertoires spécifiques à chaque évaluation;
            </li>
            <li style='line-height:1.5;'>
            <b>Vérification automatique des références pour détecter celles qui sont hallucinées par l'IA</b>. 
            L'application compare les références des étudiants avec les métadonnées disponibles sur Internet pour 
            soulever celles qui nécessitent davantage d'attention;
            </li>
            <li style='line-height:1.5;'>
            Évaluation sommaire de la qualité des références et de leur niveau de preuve en fonction du type de 
            littérature cité et de la nature des études. Ces évaluations sont sauvegardées dans la base de données 
            pour chaque étudiant pour consultation ultérieure au besoin; 
            </li>
            <li style='line-height:1.5;'>
            Génération des statistiques pour chaque étudiant relatif à la qualité des références et de leur distribution
            en fonction de l'année de publication; 
            </li>
            <li style='line-height:1.5;'>
            Mise à jour automatique du fichier GeNote;
            </li>
            <li style='line-height:1.5;'>
            Compression des fichiers relatifs à la correction pour un dépôt de la rétroaction des étudiants en 
            quelques cliques sur Moodle; 
            </li>
            <li style='line-height:1.5;'>
            Génération des statistiques pour chaque évaluation afin de comparer les notes obtenues par les étudiants et
            la qualité de leur recherche documentaire; 
            </li>
            <li style='line-height:1.5;'>
            Mécanisme d'archivage des cours. 
            </li>
            </ul>
            <p style='line-height:1.5;'>
            L'utilisation du logiciel implique évidemment une légère courbe d'apprentissage, mais la quantité de temps 
            épargnée en automatisant l'ensemble des tâches reliées à la correction est exponentielle. La première 
            chose que j'ai faite après avoir donné ma première charge de cours a été de rédiger des scripts Python pour 
            ne plus jamais avoir à modifier le nom d'un fichier pour y ajouter le nom d'un étudiant. Si vous avez 
            20 étudiants et 3 évaluations, prendre 1 minute par étudiant/évaluation en gestion de fichier de correction 
            signifie perdre 1 heure de votre temps. L'application fait ça en quelques millisecondes. 
            L'automatisation de la feuille GeNote évite les erreurs d'indexation et sauve aussi beaucoup de temps. <br>
            L'avènement de l'IA qui nous force à vérifier pratiquement 100% des références pour détecter les hallucinations
            m'a poussé à étendre les capacités de mes scripts maison pour éviter d'avoir à cliquer sur 1000 liens 
            durant la correction. Ce gain de temps se calcule en dizaine d'heure sur une session. <br>
            J'ai donc décidé de sortir mes skills de geek pour greffer une interface graphique à mes scripts Python 
            afin de produire un logiciel FOSS (open source et 100% gratuit). En espérant que cela aide à diminuer le 
            temps de correction et facilite la production de rétroactions de qualité aux étudiants. </p>  
            """)

        ebem_doi_url = "https://doi.org/10.2139/ssrn.5996094"
        self._about = FAQBlockText(
            block_question="""Pourquoi une application pour aider à la correction?""",
            block_answer=f"""
             L'objectif de l'application est d'automatiser les tâches triviales afin de se concentrer sur les éléments 
             importants des évaluations, comme la rigueur méthodologique et la qualité des références. <br>
             Devant les défis sociaux et environnementaux qui sont aggravés par les changements climatiques, il est 
             primordial de former des étudiants qui pratiquent selon les dernières données probantes. L'intelligence 
             artificielle force aussi les praticiens à redéfinir leur place afin de démontrer leur valeur ajoutée. <br> 
             La bonne nouvelle est que l'intelligence artificielle est incapable de faire de bonnes
             recommandations sur la base des meilleures données probantes tout en tenant compte du contexte complexe
             des systèmes socio-écologiques. Les praticiens en environnement sont plus pertinents que jamais malgré
             l'évolution des technologies. <br>
             Malheureusement, les pratiques actuelles dans le domaine de l'environnement ne sont pas en phase avec 
             l'état de l'art entourant la gestion de l'environnement basée sur les données probantes. Ceci n'est pas 
             une fatalité, mais cela va demander des changements importants dans les pratiques. L'application se veut 
             un pas dans cette direction en procurant une grille de correction claire pour les références, 
             ainsi que des statistiques pour calibrer les attentes. <br>
             Pour en savoir plus sur le concept de niveau de preuve, ainsi que sur les nombreux problèmes de rigueur 
             méthodologique qui afflige le domaine de l'environnement et des changements climatiques,
             il est possible de lire mon preprint sur la question (en processus de révision par les pairs) : <br>
             Côté, J.-N. (2025). Adopting Evidence-based Environmental Management to Address Climate Change: 
             Insights from Evidence-based Medicine [SSRN Scholarly Paper]. Social Science Research Network. 
             <a {HREF_STYLE} href='{ebem_doi_url}'>{ebem_doi_url}</a>
                """)

        orcid_url = "https://orcid.org/0000-0001-9629-0492"
        github_url = "https://github.com/JNCote89/"
        linkedin_url = "https://www.linkedin.com/in/jean-nicolas-cote/"
        self._contact_info = FAQBlockText(
            block_question="""Pour me rejoindre, suivre mes travaux ou signaler des bugs""",
            block_answer=f"""
            Courriel : Jean-Nicolas.Cote@USherbrooke.ca <br>
            ORCID : <a {HREF_STYLE} href='{orcid_url}'>{orcid_url}</a> <br>
            GitHub: <a {HREF_STYLE} href='{github_url}'>{github_url}</a> <br>
            LinkedIn: <a {HREF_STYLE} href='{linkedin_url}'>{linkedin_url}</a> <br>
            """)

    @override
    def _assemble_layout(self) -> None:
        self._collapsible_section.add_widget(self._features_overview)
        self._collapsible_section.add_widget(self._about)
        self._collapsible_section.add_widget(self._contact_info)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._collapsible_section)


class QuickStartCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._collapsible_section = DefaultCollapsibleSection(title="Guide de démarrage rapide")
        self._collapsible_section.content_group_box.setProperty("class", "instruction_collapsible_section")

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        genote_url = "https://www.usherbrooke.ca/genote/"
        self._genote_export_block = InstructionBlockText(
            block_title="Page 1. Création de cours - Section <i>Importation automatique de cours</i>",
            first_paragraph=f"""
            <b>Sur le site web de <a {HREF_STYLE} href='{genote_url}'>GeNote</a></b> <br>
            Avant d'exporter la feuille Excel GeNote vers l'application (encadré bleu dans l'exemple), il est très 
            important de configurer l'ensemble des évaluations (cercle rouge dans l'exemple). Sans l'ensemble des 
            évaluations, il ne sera pas possible d'automatiser l'indexation des notes par la suite.
            """,
            block_image_filename="GeNote_download.png",
            second_paragraph=""" <b>Dans l'application</b> <br>
            Glisser le fichier GeNote avec le format notes-SIGXXXGrYY-S20XX.xlsx dans l'encadré prévu à cet effet.
            <br>
            \u26A0\uFE0F Il n'est pas possible d'importer 2 fois le même cours avec les mêmes informations dans 
            l'application pour éviter la confusion. Si vous souhaitez recommencer l'importation, vous devez archiver 
            le cours dans la section <i>Archivage et suppression</i> avant de recommencer. 
             """)

        self._template_setup_block = InstructionBlockText(
            block_title="Page 2. Gestion des évaluations - Section <i>Configuration du gabarit de correction associé"
                        " à l'évaluation</i>",
            first_paragraph="""
            <b>Dans Excel (ou n'importe quel chiffrier qui génère des fichiers .xlsx)</b> <br>
            La conception d'un gabarit de correction Excel permet de préremplir une évaluation générique qui s'applique 
            à la moyenne des travaux généralement reçus. L'application va par la suite copier ce gabarit et en créer un 
            par étudiant, ce qui évite de devoir renommer des fichiers et réécrire les mêmes commentaires 50 fois. Vous 
            pouvez construire votre propre gabarit ou modifier celui fourni dans le tutoriel. L'application est 
            suffisamment flexible pour accommoder diverses feuilles, à condition de spécifier les éléments suivant :
            <ol>
                <li style='line-height:1.5;'>
                Le nom du fichier Excel qui a été importé dans le rectangle de la section précédente 
                <i>Importation des gabarits de correction Excel</i> et qui doit être associé à l'évaluation; 
                </li>
                 <li style='line-height:1.5;'>
                 Le nom de la feuille Excel qui contient la note finale (le rectangle bleu dans l'exemple sous le texte);
                 </li>
                 <li style='line-height:1.5;'>
                 Le mot clé qui identifie la rangée où se situe la note finale. Dans l'exemple, le mot clé se trouve 
                 dans le rectangle rose (Note finale);
                 </li>
                 <li style='line-height:1.5;'>
                 Le mot clé qui identifie la colonne où se situe la note finale. Dans l'exemple, le mot clé 
                 se trouve dans le rectangle orange (Notes attribuées).
                 </li>
                 </ol>
            <p style='line-height:1.5;'> 
            La triangulation du mot clé pour la rangée et la colonne permet au logiciel d'identifier la note finale à 
            importer dans GeNote à la Page 6. Gestion des notes. Dans l'exemple, la note qui sera importée est dans 
            le cercle rouge (21). Il est très important que le total ne soit pas un pourcentage, 
            il doit correspondre au nombre de points maximum qui a été attribué dans GeNote. Dans l'exemple, le plan de 
            travail est sur 25 dans GeNote, alors l'étudiant doit recevoir une note finale sur 25. Il est tout à fait
            possible de calculer le pourcentage dans la cellule adjacente comme dans l'exemple. L'utilisation de mots 
            clés plutôt que d'un index est un choix délibéré. L'adresse des cellules est très fragile à la modification 
            des grilles de correction. Avec des mots clés, l'ajout de rangées ou de colonnes n'affecte pas la 
            triangulation de la note finale, à condition de ne pas fusionner la cellule contenant la note finale et de 
            ne pas modifier l'alignement des mots clés. <br> </p>""",
            block_image_filename="Template_setup.png",
            second_paragraph="""<b>Dans l'application</b> <br>
            Il faut glisser le gabarit .xlxs construit dans l'encadré <i>Importation des gabarits de correction Excel</i>
            prévu à cet effet. L'application copie le gabarit et laisse le gabarit maître intact. 
            Il faut simplement choisir dans les menus déroulants le nom du fichier, le nom de la feuille Excel, ainsi 
            que les mots clés pour la rangée et la colonne. L'application scan les fichiers Excel qui sont importés
            pour offrir les choix possibles. Il est à noter qu'il faut importer les gabarits pour chaque cours, ce ne 
            sont pas des gabarits pour l'ensemble des cours. L'objectif est de garder un historique des versions des 
            gabarits et d'éviter de contaminer le fichier maître.  """)

        self._active_student_block = InstructionBlockText(
            block_title="Page 3. Gestion des étudiants - Statut actif/inactif",
            first_paragraph=f"""
            Si un étudiant abandonne le cours, il n'est pas possible de le supprimer. Par contre, il est possible
            de le désactiver. Cela n'efface pas les remises et les évaluations déjà effectuées, mais cela va retirer
            l'étudiant des menus déroulants pour la correction. 
            """)

        moodle_url = "https://moodle.usherbrooke.ca/"
        self._moodle_download_block = InstructionBlockText(
            block_title="Page 4. Gestion des remises étudiantes - Section <i>Importation des remises</i>",
            first_paragraph=f"""
            <b>Sur le site web de <a {HREF_STYLE} href='{moodle_url}'>Moodle</a></b> <br>
            Il faut aller dans les travaux remis, sélectionner l'ensemble des travaux (rectangle orange dans l'exemple),
            et télécharger l'ensemble des travaux étudiants (rectangle bleu dans l'exemple). Il est 
            très important de cocher l'option "Télécharger les travaux remis dans des dossiers" (cercle rouge dans 
            l'exemple). Cela permet de générer une clé aléatoire unique à 7 chiffres pour associer l'étudiant à 
            l'évaluation (e.g., 'Nom, Prénom_1234567_assignsubmission_file'). Sans cette clé, il est impossible de
            déposer une rétroaction en lot. <br> """,
            block_image_filename="Moodle_download.png",
            second_paragraph=""" <b>Dans l'application</b> <br>
            Il faut glisser le fichier .zip issu de Moodle dans l'encadré <i>Importer les travaux remis </i> 
            prévu à cet effet. 
            L'application s'occupe de décompresser la remise, puis de placer les travaux des étudiants dans leurs 
            dossiers respectifs pour la soumission. Si un gabarit de correction est correctement configuré, le 
            bouton "Générer les grilles de correction" devrait être actif et permettre de générer des fichiers Excel 
            de correction pour tous les étudiants. Ceux-ci pourront être modifiés dans la 
            Page 5. Correction et vérification des références.  """)

        self._references_block = InstructionBlockText(
            block_title="Page 5. Correction et vérification des références",
            first_paragraph=f"""Les instructions pertinentes pour importer les références sont sur la page sous les menus 
            déroulants. Pour accélérer l'évaluation des références, il est possible de naviguer avec les flèches du 
            clavier dans le tableau pour surligner la cellule à modifier, appuyer sur la barre d'espacement pour ouvrir 
            les choix dans le menu déroulant et appuyer sur entrée pour valider. Il est aussi possible d'utiliser la 
            première lettre de la valeur que l'on souhaite indexer (e.g., V pour Valide), puis entrée pour sauvegarder
            la valeur. <br>
            Pour ce qui est des algorithmes en arrière de la vérification automatique, voici les points 
            saillants :
            <ul>
            <li style='line-height:1.5;'><b>Vérification</b><br>
            L'application compare les informations des métadonnées avec les références soumises par l'étudiant. 
            L'application ne va jamais décréter qu'une référence est invalide, car des métadonnées mal formatées peuvent
            introduire des faux positifs. Pour éviter d'accuser faussement un étudiant de plagiat, il faut minimalement
            vérifier si le titre de la référence retourne un résultat dans Google. Les chances de faux négatifs sont 
            extrêmement minces, mais pourraient se produire pour un titre court générique ou une référence de la 
            littérature grise où les métadonnées sont moins riches que la littérature scientifique avec un DOI. 
            </li>
            <li style='line-height:1.5;'><b>Pertinence et alignement avec le texte</b><br>
            Cette portion doit être fait manuellement. L'utilisation des raccourcis clavier (flèches, barre d'espacement,
            entrée) permet de rapidement remplir cette section. Il est aussi possible d'utiliser le bouton en bas du 
            tableau qui permet de mettre toutes les références non évaluées à "Pertinentes et alignées". 
            </li>
            <li style='line-height:1.5;'><b>Type de littérature</b><br>
            L'API d'OpenAlex permet de classifier dans la vaste majorité du temps les articles scientifiques publiés 
            dans des journaux révisés par les pairs. Évidemment, la base de données n'est pas fiable à 100%, mais le 
            taux d'erreurs est très faible. Il est très important d'insister auprès des étudiants pour utiliser le 
            style APA 7e édition qui stipule que le DOI doit être utilisé en priorité. Le logiciel ne peut pas retracer
            le type d'article si le DOI n'est pas inscrit dans l'URL et pourrait classifier à tort un article scientifique
            comme de la littérature grise si l'URL ne convient pas 
            (e.g., l'étudiant qui cite la référence de Research Gate plutôt que l'article sur le site de l'éditeur). 
            </li>
            <li style='line-height:1.5;'><b>Niveau de preuve</b><br>
            Il est à noter que le concept de niveau de preuve est très complexe et dépend des disciplines. L'application
            fait une évaluation grossière des différents niveaux de preuve, mais le jugement de l'enseignant est requis
            pour faire l'évaluation finale. <br>
            <ol>
            <li style='line-height:1.5;'>Élevé : Revue systématique ou méta-analyse publiée dans une revue scientifique 
            révisée par les pairs. À noter que les métadonnées ne sont pas toujours fiables pour identifier les 
            revues de littérature, l'application peut classer à tort une revue systématique comme un simple article.</li>
            <li style='line-height:1.5;'>Moyen : Article scientifique publié dans une revue scientifique révisée par 
            les pairs. </li>
            <li style='line-height:1.5;'>Faible : Article scientifique non révisé par les pairs (e.g., preprint).</li>
            <li style='line-height:1.5;'>Très faible : Selon le jugement de l'enseignant. Cette catégorie existe 
            notamment pour des évaluations fines comme GRADE utilisé en médecine. </li>
            <li style='line-height:1.5;'>Aucun (Opinion d'experts/Anecdotes) : N'importe quel document issu de la 
            littérature grise. Cela ne signifie pas que la référence n'est pas pertinente (e.g., rapporter les propos des 
            parties prenantes, souligner une anecdote pertinente à l'analyse, relever les pratiques courantes, etc.), 
            mais on ne peut pas appuyer une analyse, une recommandation ou une conclusion seulement sur la base 
            de la littérature grise ou d'une opinion d'experts.</li>
            </ol>
            <br>
            <li style='line-height:1.5;'><b>Année</b><br>
            L'application ne fait pas la vérification automatique de la date, car la littérature
            grise retournait trop de métadonnées vides pour être utile. Ainsi, la date se fie sur la citation étudiante.
            <br>
            Il peut y avoir une différence d'un an pour les articles scientifiques qui sont publiés en ligne vers 
            la fin de l'année, puis publiés en version papier en début d'année. Il n'y a pas toujours de constance 
            dans les métadonnées à cet égard, il ne faut pas pénaliser si la date dans la colonne des métadonnées 
            retourne un résultat à \U000000B1 1 an près.  
            </li>
            
            """)

        self._genote_upload_block = InstructionBlockText(
            block_title="Page 6. Gestion des notes - Sous-section <i>Compiler les notes des "
                        "étudiants dans la feuille Excel GeNote</i>",
            first_paragraph=f"""
            Lorsque la correction de l'ensemble des travaux pour l'évaluation est terminée, il est possible
            d'actualiser automatiquement la feuille GeNote en cliquant sur le bouton "Mettre à jour le fichier GeNote".
            Grâce aux mots clés définis précédemment à la page 2. Gestion des évaluations, l'application peut compiler 
            les notes de chaque étudiant. Une fois la compilation effectuée, cliquez sur le 
            lien en bas du bouton menant au répertoire GeNote et faites une vérification manuelle du fichier
            (il peut y avoir des erreurs, puisqu'il y a parfois des disparités entre les noms des étudiants sur 
            Moodle et GeNote). Si les notes sont correctes, vous pouvez déposer le fichier GeNote actualisé sur 
            le site web de <a {HREF_STYLE} href='{genote_url}'>GeNote</a> (rectangle orange dans l'exemple).
            """,
            block_image_filename="GeNote_upload.png")

        self._moodle_upload_block = InstructionBlockText(
            block_title="Page 6. Gestion des notes - "
                        "Sous-section <i>Compresser les fichiers de correction pour les déposer en lot sur Moodle</i>",
            first_paragraph=f"""
            Pour générer les rétroactions compatibles avec Moodle, il suffit de cliquer sur le bouton 
            "Générer le fichier .zip de rétroaction pour Moodle". L'application va compresser l'ensemble des 
            dossiers de rétroactions avec la clé associé à chaque étudiant. En cliquant sur le lien sous le bouton, 
            vous pourrez récupérer le fichier .zip à déposer sur <a {HREF_STYLE} href='{moodle_url}'>Moodle</a></b>.
            Il ne faut pas décompresser le fichier, Moodle s'en charge. 
            """,
            block_image_filename="Moodle_upload.png")

        self._archive_block = InstructionBlockText(
            block_title="Page Archivage et suppression",
            first_paragraph=f"""La procédure pour supprimer un cours nécessite 3 étapes : 
            <ol>
            <li style='line-height:1.5;'>Cliquer sur le bouton "Archiver le cours sélectionné" qui compressera 
            l'ensemble des fichiers du cours sur votre disque dur en plus d'extraire le cours de la base de données.
            </li>
            <li style='line-height:1.5;'> Supprimer le fichier compressé (.zip) dans les archives de l'application (le
            lien est disponible sur la page, c'est un répertoire qui est créé au même niveau que les semestres sous
            le répertoire principale PyCorrection).
            </li>
            <li style='line-height:1.5;'>
            Supprimer le fichier compressé dans la corbeille de votre système d'exploitation.
            </li> 
            </ol>
            <p style='line-height:1.5;'> 
            Si vous souhaitez faire la procédure inverse, vous pouvez restaurer le fichier .zip de l'archive en le 
            glissant dans l'encadré <i>Restaurer un cours archivé</i> prévu à cet effet. Il ne faut pas modifier
            ou décompresser ce fichier .zip, 
            sinon la restauration ne fonctionnera pas (l'application a besoin du fichier .db et manifest.json intact à 
            l'intérieur du fichier .zip pour faire la restauration). Par contre, vous pouvez extraire les travaux
            étudiants et la feuille GeNote manuellement pour consultation à l'extérieur de l'application sans problème. 
            </p>
            """)

        self._delete_files_block = InstructionBlockText(
            block_title="Quels fichiers peuvent être supprimés en cas d'erreur d'importation?",
            first_paragraph="""L'application ne peut pas effectuer de vérification pour s'assurer que l'importation des
            fichiers .zip en provenance de Moodle correspondent bel et bien à l'évaluation active, puisque l'application
            ne contrôle pas le nom des fichiers externes. Il en va de même pour l'importation des gabarits de correction.
            En cas d'erreurs, il est toujours possible de supprimer les fichiers Moodle des étudiants qui ont le format 
            suivant -> "Nom, Prénom_1234567_assignsubmission_file". Par contre, il ne faut pas supprimer les répertoires
            de l'application (Remises étudiantes, Corrections, etc.)
            """)

    @override
    def _assemble_layout(self) -> None:
        self._collapsible_section.add_widget(self._genote_export_block)
        self._collapsible_section.add_widget(self._template_setup_block)
        self._collapsible_section.add_widget(self._active_student_block)
        self._collapsible_section.add_widget(self._moodle_download_block)
        self._collapsible_section.add_widget(self._references_block)
        self._collapsible_section.add_widget(self._genote_upload_block)
        self._collapsible_section.add_widget(self._moodle_upload_block)
        self._collapsible_section.add_widget(self._archive_block)
        self._collapsible_section.add_widget(self._delete_files_block)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._collapsible_section)


class OptionsCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._collapsible_section = DefaultCollapsibleSection(title="Descriptions des options de configuration")
        self._collapsible_section.content_group_box.setProperty("class", "instruction_collapsible_section")

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._configuration_options = OptionsBlockText(
            block_title="Page Configurations",
            block_text="""
            <ul>
            <li style='line-height:1.5;'> <b>Répertoire racine </b><br>
                Chaque importation de cours génère une arborescence de répertoires pour classer les fichiers relatifs 
                à chaque cours selon l'ordre suivant :
               <div>\U0001F4C1 Répertoire racine</div>
               <div style='margin-left: 10px;'>\U0001F4C1 PyCorrection</div>
               <div style='margin-left: 20px;'>\U0001F4C1 Semestre (e.g., A2026)</div>
               <div style='margin-left: 30px;'>\U0001F4C1 Cours (e.g., ENV847)</div>
               <div style='margin-left: 50px;'>\U0001F4C2 Groupe (e.g., Groupe - 99)</div>
               <div style='margin-left: 55px;'>\U0001F4C1 Corrections</div>
               <div style='margin-left: 55px;'>\U0001F4C1 Gabarits de correction</div>
               <div style='margin-left: 55px;'>\U0001F4C1 GeNote</div>
               <div style='margin-left: 55px;'>\U0001F4C1 Remises étudiantes</div>
               <p style='line-height:1.5;'>   
               Il est possible d'avoir accès à l'ensemble de ces répertoires autant via les liens dans l'application 
               qu'en utilisant le navigateur de fichiers de votre système d'exploitation. 
               <br>
               \u26A0\uFE0F Il ne faut pas changer le répertoire racine une fois les répertoires créés, sinon 
               l'application ne peut pas retrouver les fichiers relatifs au cours. Pour changer le répertoire racine, 
               il faut archiver le cours, changer le répertoire racine et réimporter le cours 
               (l'arborescence se régénère lors de la restauration du cours). 
            </li>
            <li style='line-height:1.5;'> <b>Mode de remplissage automatique des gabarits de correction </b><br>
            Afin d'éviter de devoir configurer les gabarits de correction à chaque nouveau cours, il est possible
            d'activer le remplissage automatique des gabarits basés sur l'historique d'utilisation. Lors de la sélection
            du fichier Excel, l'application peut détecter si les mots clés pour la rangée et la colonne ont déjà été 
            importés dans un cours précédent pour la même évaluation. Si oui, les paramètres se remplissent 
            automatiquement. Il est toujours possible de les changer manuellement par la suite. 
            </li>
            <li style='line-height:1.5;'> <b>Style de citation pour les références </b><br>
            Pour le moment, seul le style APA 7e édition est disponible. En théorie, n'importe quel style CSL peut être 
            ajouté, mais cela demande du temps, puisqu'il y a beaucoup de codes à produire pour convertir le texte 
            en citation et couvrir tous les cas limites. 
            </li>
            <li style='line-height:1.5;'> <b>Afficher les notifications explicatives </b><br>
            Par défaut, l'application génère plusieurs popup explicatifs pour accompagner les utilisateurs. Il est 
            possible de désactiver l'ensemble des explications lorsque vous êtes familiers avec les différentes 
            fonctionnalités de l'application. Les explications demeurent disponibles dans la console en tout temps et
            les popup pour confirmer les opérations demeurent toujours en vigueur. 
            </li>
            <li style='line-height:1.5;'> <b>Développer les sections manuelles </b><br>
            Par défaut, les sections manuelles sont cachés pour réduire la surcharge visuelle. Ces sections ne 
            devraient être utilisées qu'en l'absence d'une feuille GeNote (e.g., pour accompagner des étudiants aux
            études graduées ou pour des projets spéciaux).
            </li>
               <p>
               """)

    @override
    def _assemble_layout(self) -> None:
        self._collapsible_section.add_widget(self._configuration_options)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._collapsible_section)


class FAQCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._collapsible_section = DefaultCollapsibleSection(title="F.A.Q")
        self._collapsible_section.content_group_box.setProperty("class", "instruction_collapsible_section")

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._quick_reference_check_qa = FAQBlockText(
            block_question="""Comment puis-je faire une vérification rapide de références?""",
            block_answer="""Il est possible de se créer un cours fictif sans étudiants et sans évaluations pour seulement 
            vérifier des références. Cependant, aucun résultat ne sera sauvegardé. Si vous souhaitez sauvegarder les 
            résultats, vous pouvez vous ajouter comme étudiant dans le cours fictif et ajouter des évaluations
            correspondant à vos besoins. 
            """)

        self._team_submission_qa = FAQBlockText(
            block_question="""Comment puis-je gérer les travaux d'équipe?""",
            block_answer="""Moodle ne rend pas facile la gestion des travaux d'équipe, car chaque étudiant doit
            absolument déposer quelque chose pour générer une clé aléatoire à 7 chiffres qui change à chaque évaluation
            et dont l'application a besoin pour associer les travaux aux notes des étudiants 
            (e.g., 'Nom, Prénom_1234567_assignsubmission_file'). Il faut donc demander à chaque étudiant de déposer 
            quelque chose (e.g., une fiche de plagiat, un contrat d'équipe, etc.), générer les grilles de correction 
            comme si c'était un travail individuel et copier-coller l'évaluation effectuée à tous les membres de l'équipe. 
            """)

        self._delete_button_qa = FAQBlockText(
            block_question="""Pourquoi n'y a-t-il pas de fonctions pour supprimer des cours, des évaluations ou
            des étudiants?""",
            block_answer="""L'absence de bouton supprimé n'est pas un bug, c'est un feature. L'idée est d'éviter
            la suppression accidentelle de fichiers importants en introduisant un maximum de friction. Mieux vaut une 
            suppression en 3 étapes dont les 2 premières sont réversibles qu'effacer 10 heures de travail de correction!    
            """)

        self._other_template_format_qa = FAQBlockText(
            block_question="""Pourquoi ne pouvons-nous pas utiliser d'autres formats qu'Excel pour les gabarits de
            correction?""",
            block_answer="""L'objectif de l'application est de travailler efficacement! Il n'y a aucun monde où utiliser
            un gabarit Word ou PDF permet de sauver du temps. Les fichiers Excel permettent de tout calculer 
            automatiquement sans risque d'erreurs et permettent d'aisément mettre à jour la feuille 
            GeNote (ce qui n'est pas possible avec des formats .docx ou .pdf). Il est tout à fait possible de joindre 
            un fichier Word ou PDF annoté avec la grille Excel. L'application va compresser l'ensemble des fichiers 
            dans le répertoire de correction et l'étudiant aura accès autant à la grille Excel qu'au travail annoté.
            """)

        github_url = "https://github.com/JNCote89/"
        self._stack_qa = FAQBlockText(
            block_question="""Quel est le stack utilisé pour l'application?""",
            block_answer=f"""
            L'ensemble du code Python est disponible sur mon GitHub <a {HREF_STYLE} href='{github_url}'>{github_url}</a> . 
            Les principales bibliothèques utilisées sont PySide6 pour le GUI, SQLite pour la base
            de données, openpyxl pour gérer les gabarits de correction et la feuille GeNote, pypandoc 
            pour gérer les styles bibliographiques et l'importation de fichiers bibtext, 
            ainsi que les API de CrossRef (habanero) et OpenAlex pour la vérification 
            des références. L'application a été compilée avec Nuitka et est signée digitalement par la 
            SignPath Foundation.
            """)

        self._engine_qa = FAQBlockText(
            block_question="""Est-ce que l'IA générative est utilisée pour évaluer les références?""",
            block_answer=f"""
            Aucune IA générative n'est utilisée pour vérifier les références. L'ensemble des vérifications sont issues 
            d'un algorithme simple en Python. L'objectif est de garder l'application gratuite avec une faible empreinte 
            environnementale. De plus, les IA génératives ne sont pas performantes pour évaluer le niveau de preuve.
            La qualité des références est évaluée en fonction des métadonnées tirées de CrossRef
            et OpenAlex. Ainsi, il demeure primordial que le jugement de l'enseignant s'applique pour faire l'évaluation
            finale. 
            """)

        self._ai_use_qa = FAQBlockText(
            block_question="""Est-ce que l'application a été 'vibe codé' avec des agents d'IA génératifs?""",
            block_answer="""Non, l'architecture de l'application a été créé par moi à 100%, pour le meilleur
            et pour le pire. Je ne suis pas un ingénieur logiciel, je suis seulement un geek avec un PhD en modélisation
            géospatiale. Gemini 3.5 a été utilisé pour le "boilerplate code" (e.g., filtres regex, méthode pour modifier
            des widgets spécifiques, etc.), mais chaque ligne de code a été révisée et validée par moi. 
            """)

        self._macos_qa = FAQBlockText(
            block_question="""Pourquoi n'y a-t-il pas de version pour macOS?""",
            block_answer="""Apple étant une entreprise basée sur l'obsolescence programmée et hostile à tout ce qui ne 
            permet pas d'extorquer les utilisateurs, je n'avais aucun moyen de tester l'application gratuitement 
            pour l'écosystème de macOS. Le code a été développé sur Linux, mais GitHub Actions me permet de compiler 
            une version Windows que j'ai testée dans une machine virtuelle avec Windows 10.
            """)

        self._license_qa = FAQBlockText(
            block_question="""Puis-je réutiliser/modifier le code?""",
            block_answer=f"""Oui! Le projet est à 100% FOSS (free and open source). Vous êtes libre de "forker" le code.
            Si vous trouvez le lancement de l'application trop lent, il est possible de le compiler 
            pour votre machine ou simplement rouler le code Python dans un environnement virtuel afin d'éviter de 
            recharger les bibliothèques nécessaires au programme à chaque lancement. J'ai privilégié la compatibilité et
            la facilité d'utilisation au détriment de la performance, mais rien ne vous empêche de personnaliser 
            votre usage de l'application pour vos besoins.""")

        self._delay_qa = FAQBlockText(
            block_question="""Pourquoi est-ce que chaque vérification de référence prend 0,5 seconde?""",
            block_answer=f"""
            Il serait théoriquement possible de vérifier l'ensemble des références plus rapidement.
            Cependant, pour éviter de surcharger les serveurs et risquer un bannissement de l'IP sur la base d'un
            web scrapping trop agressif, un délai ferme de 0,5 seconde est codé entre chaque requête. 
            """)

    @override
    def _assemble_layout(self) -> None:
        self._collapsible_section.add_widget(self._quick_reference_check_qa)
        self._collapsible_section.add_widget(self._team_submission_qa)
        self._collapsible_section.add_widget(self._delete_button_qa)
        self._collapsible_section.add_widget(self._other_template_format_qa)
        self._collapsible_section.add_widget(self._stack_qa)
        self._collapsible_section.add_widget(self._engine_qa)
        self._collapsible_section.add_widget(self._ai_use_qa)
        self._collapsible_section.add_widget(self._macos_qa)
        self._collapsible_section.add_widget(self._license_qa)
        self._collapsible_section.add_widget(self._delay_qa)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._collapsible_section)
