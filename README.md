<!-- fork-aviso: início. Bloco adicionado neste fork; o texto original do upstream começa abaixo. -->
> **Sobre este repositório.** Fork de [anonymous-programmers/BugReportAssignment](https://github.com/anonymous-programmers/BugReportAssignment), o repositório anonimizado do dataset de bug reports e commits associado ao artigo "Improving Developer Profiling to Enhance Bug Report Assignment" (ICPC 2019) e a Alkhazi et al. (Applied Soft Computing, 2020). O dump `SQL_BugDatabase_Dump.7z`, `ExtractedFeatures.zip` e `SVMrank_Models.zip` vêm do upstream sem alteração.
>
> O upstream não traz arquivo de licença; consulte-o para os termos de uso dos dados. O dump contém bug reports e histórico de commits de projetos open source (segundo o README do upstream) e inclui nomes de usuários e desenvolvedores.
>
> O que é deste fork: a análise exploratória para uma dissertação de mestrado (`scripts/`, `outputs/`, `NOTES.md`, `DECISIONS.md`, `dissertacao/`). Esses arquivos trazem só dados agregados; amostras com nomes pseudonimizados, se existirem, ficam em `data/samples/`.
<!-- fork-aviso: fim -->

# Introduction
This document contains links and instructions regarding the dataset and approach we used as described in the ICPC 2019 paper “Improving Developer Profiling to Enhance Bug Report Assignment.”  The dataset contains bug reports and the corresponding commit history for the six open source Java projects: AspectJ, Birt, Eclipse Platform UI, JDT, SWT, and Tomcat.  Where applicable, we have provided files from both our replication of Tian et al.'s approach as well as our novel approach. These files are split into two folders: "OurNewApproach" (containing files from our approach) and "PreviousApproach" (containing files from our recreation of the previous approach).

# How to obtain the dataset
Download the dataset.zip archive from the link below:

[https://github.com/anonymous-programmers/BugReportAssignment/blob/master/SQL_BugDatabase_Dump.7z](https://github.com/anonymous-programmers/BugReportAssignment/blob/master/SQL_BugDatabase_Dump.7z)

Once unzipped, the dataset folder will contain a SQL dump that, when run, will create the database and tables, and populate the tables with data.

# Database Structure
This section describes the structure of the bug_commit table, which is the table primarly used for information extraction for each bug report.

 - id: A database assigned ID number (has no meaning outside of this database)
 - bug_id: The ID number associated with the bug report
 - summary: The short bug report summary/title
 - description: The long, extended description about the bug report
 - report_time: The timestamp that the bug report was created
 - reporter: The user who created the bug report
 - assignee: The developer who the bug report was assigned to
 - status: The status of the bug report (e.g. VERIFIED FIXED)
 - product: The product to which the bug report refers
 - component: The subsection of the product to which the bug report refers
 - importance: A scale indicating the severity of the bug and the urgency of the ensuing fix
 - commit: The commit hash of the commit that resolved the bug report
 - author: The developer who wrote the code & commit that resolved the bug report 
 - commit_time: The timestamp that the commit that fixed the bug report was submitted
 - log: The commit message submitted with the code changes
 - files: A list of filenames that were changed in the commit

# How to obtain the Source Code
To obtain the sorce code, run *git clone* commmands on the following URLs and then checkout to a given commit hash:
1. **AspectJ**: [https://github.com/eclipse/org.aspectj.git](https://github.com/eclipse/org.aspectj.git)
2. **Birt**: [https://github.com/eclipse/birt.git](https://github.com/eclipse/birt.git)
3. **Eclipse Platform UI**: [https://github.com/eclipse/eclipse.platform.ui.git](https://github.com/eclipse/eclipse.platform.ui.git)
4. **JDT**: [https://github.com/eclipse/eclipse.jdt.core.git](https://github.com/eclipse/eclipse.jdt.core.git)
5. **SWT**: [https://github.com/eclipse/eclipse.platform.swt.git](https://github.com/eclipse/eclipse.platform.swt.git)
6. **Tomcat**: [https://github.com/apache/tomcat.git](https://github.com/apache/tomcat.git)

# Efficient Indexing of the Code
Per Ye et al.:

If bug 420972 is the first bug processed by the system, we check out its before-fix version 2143203 and index all the corresponding source files. To process another bug report 423588, we need to check out its before-fix version 602d549 of the source code package. For efficiency reasons, we do not need to index all  the  source  files again. Instead, we index only the changed files, i.e., files that were “Added”, “Modified”, or “Deleted” between the two bug reports. The changed files can be obtained as follows:
 - **Added**: *git diff --name-status 2143203 602d549 | grep ".java$" | grep "^A"*
 - **Modified**: *git diff --name-status 2143203 602d549 | grep ".java$" | grep "^M"*
 - **Deleted**: *git diff --name-status 2143203 602d549 | grep ".java$" | grpe "^D"*

# Extracted Feature Values
The .CSV files containing our extracted feature values can be found at: 

[https://github.com/anonymous-programmers/BugReportAssignment/blob/master/ExtractedFeatures.zip](https://github.com/anonymous-programmers/BugReportAssignment/blob/master/ExtractedFeatures.zip)

# SVMrank Model
We have provided the models created as a result of training Joachims' learning to rank model on historical bug fixing data.  Additionally, we have included our extracted features formatted into .dat files that can be inputted into the model to generate ranking outputs.  For more information on the SVMrank tool, see [https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html). Our models and .dat files can be found here:

[https://github.com/anonymous-programmers/BugReportAssignment/blob/master/SVMrank_Models.zip](https://github.com/anonymous-programmers/BugReportAssignment/blob/master/SVMrank_Models.zip)

# Deep Learning Azure Project
The Azure Machine Learning Project used to create our Deep Learning based results is made available in the Azure AI Gallery at the link below. The Experiment trains an Ordinal Regression Model on all 9 binary classifiers for comparison, but only the boosted decision tree classifier is used in our study. Please note that this repository is unlisted and can only be viewed from the link below:

(Link Omitted for Double Blind Review as it reveals author identity)
