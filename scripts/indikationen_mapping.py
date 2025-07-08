# -*- coding: utf-8 -*-
import re

def create_indication_mapping():
    """
    Parst die Quelldaten und erstellt ein Dictionary, das ICD-10-Codes 
    auf ihre jeweiligen Indikationstexte abbildet.

    Diese überarbeitete Funktion verwendet eine robustere Methode mit re.finditer,
    um die Textblöcke sicher zu extrahieren und Fehler zu vermeiden. Sie 
    behandelt mehrere Codes in einer Zeile, indem sie für jeden einen 
    eigenen Eintrag erstellt.

    Returns:
        dict: Ein Dictionary, bei dem die Schlüssel die ICD-10-Codes (str) 
              und die Werte die zugehörigen, unveränderten Textblöcke (str) sind.
    """
    # Der gesamte Quelltext wird in diesem mehrzeiligen String gespeichert.
    # Der erste, redundante C34-Block wurde wie gewünscht entfernt.
    source_text = r"""
C79.5, C78.0, C78.7, C79.86, C79.9: 
Oligometastasierung:
Metachrone Oligometastasierung
Die randomisierte SABR-COMET Studie zeigte, dass bei Patienten mit kontrolliertem Primärtumor und bis zu 5 Fernmetastasen die stereotaktische Radiotherapie (SBRT) aller Metastasen zusätzlich zur standard of care Systemtherapie zu einem klinisch bedeutsamen und statistisch signifikanten Überlebensvorteil mit einem Hazard Ratio von 0.47 führte.
Palma, D. A. et al. (2020) ‘Stereotactic Ablative Radiotherapy for the Comprehensive Treatment of Oligometastatic Cancers: Long-Term Results of the SABR-COMET Phase II Randomized Trial’, Journal of clinical oncology: official journal of the American Society of Clinical Oncology, p. JCO2000818.
    
Synchrone Oligometastasierung
Die randomisierten Studien von Gomez et al. bzw Iyengar et al. zeigten, dass Patienten mit nicht-kleinzelligem Bronchialkarzinom (NSCLC) und maximal 3 bis 5 Fernmetastasen, die nach Erstlinien Systemtherapie eine stabile Erkrankung oder eine partielle Remission zeigten, durch eine konsolidierende stereotaktische Radiotherapie (SBRT) aller Metastasen zusätzlich zur standard of care Erhaltungstherapie ein signifikant längeres progressionsfrei Überleben und Gesamtüberleben haben.
Gomez, D. R. et al. (2020) ‘Local consolidative therapy versus maintenance therapy or observation for patients with oligometastatic non-small-cell lung cancer without progression after first-line systemic therapy: long-term results of a multiinstitutional, phase II, randomised study’, Journal of Clinical Oncology 37, no. 18 1558-1565.
Iyengar, P. et al. (2018) ‘Consolidative radiotherapy for limited metastatic non-small-cell lung cancer: A phase 2 randomized clinical trial’, JAMA Oncology, 4(1). doi: 10.1001/jamaoncol.2017.3501.
Zur Verbesserung der lokalen Kontrolle (inkl. Symptomkontrolle), des progressionsfreien Überlebens und auch des Gesamtüberlebens besteht somit bei synchroner und metachroner Oligometastasierung die Indikation zur stereotaktischen Strahlentherapie.

Oligoprogression:
Aufgrund der Prognose (antizipiert > 6 Monate), der kürzeren Therapiedauer, des günstigen Toxizitätsprofils und der höheren biologischen Dosis ist bei Oligoprogression der stereotaktischen Strahlentherapie (SBRT) der Vorzug gegenüber einer palliativ dosierten konventionellen Strahlentherapie zu geben, um eine langfristige lokale Tumorkontrolle und eine Verbesserung des progressionsfreien Überlebens zu ermöglichen.

Polymetastasierung:
Für Patienten mit multipler Metastasierung, die eine antizipierte Lebenserwartung von mehr als sechs Monaten haben und eine palliative Strahlentherapie indiziert ist, sollte für eine dauerhafte Symptomkontrolle und längerfristige lokale Kontrolle zur Vermeidung von Komplikationen durch eine lokale Progression die Indikation für eine stereotaktische Strahlentherapie geprüft werden.

Radiotherapie Palliativ Knochen:
Rechtfertigende Indikation: ASTRO –Guidelines for Palliative Radiotherapy for Bone Metastases (http://dx.doi.org/10.1016/j.ijrobp.2010.11.026), Cochrane Review 2008, Issue 4 :Palliation of metastatic bone pain: single fraction versus multifraction radiotherapy
Einschlusskriterien: Schmerzen, drohende Komplikationen (Fraktur, Myelonkompression, Nervenkompression).

C64:
Primäre SBRT Nierenzellkarzinom: Mehrere prospektive Phase-II Studien haben ein sehr gutes onkologisches Outcome der Stereotaktischen Bestrahlung des Nierenzellkarzinom gezeigt. Somit ist die SBRT bei Patienten mit lokal begrenztem Nierenzellkarzinom eine kurative Therapieoption.
Rühle ctRO 2019, Siva BJU Int 2017, Correa Eur Urol Focus 2019

C67:
Trimodel Therapie Indikation:
Die trimodale Therapie (TUR-B, Radiotherapie, Chemotherapie), stellt beim lokalisierten, muskelinvasiven Harnblasenkarzinom (cT2-4 cN0 cM0) die einzige organerhaltende, kurative Therapieoption und eine Alternative zur radikalen Zystektomie dar.
Hierbei ist die kombinierte Radiochemotherapie gegenüber der alleinigen Radiotherapie bezüglich lokaler Kontrolle überlegen. Somit ist für das muskelinvasive Harnblasenkarzinom die Radiochemotherapie nach TURB gemäss S3- und NCCN-Leitlinie eine kurative Therapiemöglichkeit bei inoperablen PatientInnen sowie bei Wunsch nach Organerhalt.
NCCN, S3, James 2012, Hall 2017, Coppin 1996

C24:
RT neoadjuvant vor geplanter Transplantation beim nicht resektablen perihilären CCC : Mayo-Protokoll
Beim nicht resektablen perihilären CCC, < 3 cm Grösse und ohne Nachweis von LK-Befall, kann die Lebertransplantation evaluiert werden. Dabei konnte mittels neoadjuvanter Radiochemotherapie (Capecitabine, dieses wird auch nach der RCHT fortgeführt) eine deutliche Verbesserung des Überlebens dieser Patienten erzielt werden, weshalb die neoadjuvante RCHT ein elementarer Bestandteil dieses Therapie-Konzeptes ist.
Rosen et al, 2010, Tan et al, 2020 (Update)


Nicht-resektables CCC:
Beim nicht-resektablen Cholangiokarzinom kann bei Patienten, die auf eine initiale systemische Therapie über mehrere Monate, nicht progredient sind, eine Lokaltherapie zur Verbesserung der Lokalkontrolle evaluiert werden. Die Radiotherapie konnte dabei in einer kürzlich erschienen Systematischen Übersichtsarbeit eine gepoolte 1-Jahres-Lokalkontrollraten von 79% erzielen.
Das Fraktionierungsschema sollte dabei in Abhängigkeit der Lage und Grösse gewählt werden.
NCCN-Guidelines Hepatobiliary 2020, Lee al, 2019


Adjuvante Radio(chemo)Therapie nach Resektion:
Insgesamt ist die Datenlage zur adjuvanten Radiochemotherapie beim resezierten CCC inkonsistent. In Abwesenheit von Phase-III-Studien ist die Radiochemotherapie als mögliche therapeutische Alternative zur adjuvanten Systemtherapie oder Anschlussbehandlung nach Chemotherapie bei R1-Resektions- oder positivem LK-Status erwähnt.
NCCN-Guidelines Hepatobiliary 2020


Palliativ:
Eine palliative Bestrahlung von Cholangiozellulären Karzinomen kann zur Symptomkontrolle indiziert werden.
NCCN-Guidelines Hepatobiliary 2020

C22:
SBRT als Lokaltherapie:
Bei Patienten mit HCC, die nicht für eine Leber-Transplantation oder Resektion qualifizieren, sollte eine Lokaltherapie diskutiert werden. Dabei ist die SBRT in Guidelines als Alternative zu anderen Lokalverfahren (Ablation, Embolisation) erwähnt, insbesondere, wenn aufgrund der Tumorgrösse (> 3 cm) oder Lokalisation mit Nähe zu grossen Gefässen oder Gallenwegen das Lokalrezidiv-Risiko von Thermal-Ablativen Verfahren hoch ist. In einer Metaanalyse konnte mittels SBRT eine gepoolte Lokalkontrollrate von 84% nach 2 Jahren gezeigt werden.
(NCCN-Guidelines Hepatobiliary 2020, ESMO Guidelines 2019, Rim et al, 2019)
Eine Lokaltherapie kann auch als Bridging-Verfahren eingesetzt werden mit dem Ziel die Drop-out Rate von der Transplantations-Liste aufgrund Tumorprogress zu verringern. Es gibt keine prospektiven Studien, die verschiedene Lokaltherapie-Verfahren miteinander vergleichen. In einer retrospektiven Analyse war die SBRT zu anderen Lokalverfahren (RFA, TACE) gleichwertig hinsichtlich Rate an tatsächlich erfolgter Leber-Transplantation, postoperativen Komplikationen oder Gesamt-Überleben obschon Patienten, die der SBRT zugeführt wurden, aufgrund der verminderten Leberfunktion keine Kandidaten für ein anderes Therapie-Verfahren waren.
(Sapisochin et al, 2017)
Bei fortgeschrittenen HCC ohne Möglichkeit einer Resektion oder Transplantation kann eine Radiotherapie, kombiniert zu einer TACE evaluiert werden. In einer kleinen randomisieren Studie war dies der alleinigen Sorafenib Therapie überlegen.
(Yoon et al, 2018)

RT neoadjuvant vor Resektion:
Vaskuläre Thromben sind als Risikofaktor für ein schlechteres Outcome bei HCC bekannt. Bei resezierbaren HCC-Tumoren mit Vorliegen eines Portalvenen-Thrombus konnte durch eine neoadjuvante Bestrahlung ein besseres krankheits-freies und Gesamtüberleben gezeigt werden.
(Wei et al, 2019).

Palliativ:
Eine palliative Bestrahlung von Lebertumoren kann zur Symptomkontrolle indiziert werden.


C15:
Ösophagus Primär-definitive Radiochemotherapie:
Bei lokal fortgeschrittenen anatomisch oder funktionell inoperablen Tumoren stellt die Radiochemotherapie die einzige kurative Therapieoption dar. Bei operablen Tumoren verbessert die zusätzliche Operation nach Radiochemotherapie die lokale Kontrolle, jedoch nicht das Gesamtüberleben, so dass eine definitive Radiochemotherapie, je nach Risikoprofil, eine geeignete Therapiealternative bietet und gemäss S3-Leitlinie eine Standardtherapie darstellt.
S3-Leitlinie V2.01-10/2018, Stahl M. J Clin Oncol. 2005, Bedenne et al, J Clin Oncol. 2007
Ab Stadium IIB als Alternative zur Operation generell zu diskutieren, insbesondere bei Plattenepithelkarzinomen des oberen und mittleren Drittels (Patientenwunsch/OP-Morbidität abzuwägen).
Bei inoperablen Tumoren RCT als einzige weitere kurative Option (Pöttgen et al Cancer Treat Rev. 2012).

Ösophagus neoadjuvante Radiochemotherapie:
Bei lokal fortgeschrittenen operablen Tumoren des Oesophagus und des oesophagogastralen Überganges ab St. IIB verbessert eine präoperative Radiochemotherapie hochsignifikant mit einer HR von 0.657 das Gesamtüberleben unabhängig vom histologischen Subtyp gegenüber einer alleinigen Operation. Somit ist beim lokal fortgeschrittenen operablen Oesophaguskarzinom die neoadjuvante Radiochemotherapie vor Operation gemäss S3-Leitlinie die Standardtherapie.
Van Hagen et al., CROSS Trial, NEJM. 2012/2015, S3-Leitlinie V2.01-10/2018

Ösophagus palliative Brachytherapie:
Ösophageale palliative Brachytherapie ist eine Strahlentherapietechnik, mit der der Tumor mit einer hohen Strahlendosis bestrahlt wird. Dabei bleibt bei einer hohen Oberflächendosis die Dosis auf das umliegende Gewebe relativ gering. Das Ziel der palliativen Brachytherapie ist Linderung der Dysphagie.
Eine Meta-Analyse zeigte ein DyFS (dysphagia-free survival) von 67% nach 3 Monaten, 47% nach 6 Monaten, und 29% nach 12 Monaten. Ca. 12% den Patienten entwickeln eine Brachytherapiebedingte Stenose und 8% eine Fistel entwickelt (Fucio 2017). Eine Literaturübersicht berichtet von einem mittleren DyFS von 99 Tagen (Lancellotta 2020).


C20:
Beim Rektumkarzinom des unteren und mittleren Drittels senkt ab UICC Stadium II die zusätzliche Radiochemotherapie die Lokalrezidivrate signifikant und erhöht für Tumore des unteren Rektumdrittels die Rate an Sphinktererhalt. Die neoadjuvante Radiochemotherapie ist bei verbesserter lokaler Kontrolle und geringerer Toxizität gemäss des CAO/ARO/AIO-94 einer postoperativen Radiochemotherapie überlegen. Somit ist beim lokal fortgeschrittenen Rektumkarzinom, insbesondere des unteren Drittels die neoadjuvante Radiochemotherapie vor Operation gemäss S3-Leitlinie die Standardtherapie.
Sauer 2004, Sauer et al, 2012, S3-Leitlinie

Bei lokal fortgeschrittenen operablen Tumoren des Rektums verbessert die Vorbehandlung mit einer kurzzeitigen Radiotherapie die Lokalrezidivrate. Somit ist beim lokal fortgeschrittenen Rektumkarzinom eine neoadjuvante Radiotherapie vor Operation gemäss S3-Leitlinie eine Standardtherapie. Eine Kombination mit einer konsolidierenden Chemotherapie ist möglich.
Folkesson et al 2005, Stockholm III, Bujko 2016

C25:
SBRT bei Pankreaskarzinom:
Bei inoperablen lokal fortgeschrittenen Pankreaskarzinomen stellt die Ablative Bestrahlung in Form einer SBRT eine gute Therapeutische Option mit hohen lokalen Kontrollraten dar (1-Jahres-Kontrollrate von 72.3 % in einer gepoolten systematischen Analyse). Diese Therapie sollte daher allen Patienten mit inoperablem Pankreaskarzinom, welches auf eine initiale mindestens 4-6-monatige Systemtherapie nicht progredient ist, angeboten werden.
Systematic Review, Petrelli et al., 2017, NCCN Guidelines, ASTRO Guidelines

Beim symptomatischem Pankreaskarzinom kann eine lokale Bestrahlung des Primärtumors zur Linderung der Beschwerden führen. Dabei kann eine moderate Dosisintensivierung mittels SBRT im Rahmen der offenen klinischen Studie durchgeführt werden (MASPAC trial).




Kombinierte Radiochemotherapie bei lokal fortgeschritten inoperabel (LAPC):
Bei inoperablen lokal fortgeschrittenen Tumoren führt eine Bestrahlung zu einer Verbesserung der lokalen Tumorkontrolle. Falls eine SBRT nicht möglich ist, kann in diesem Fall bei Patienten mit inoperablem Pankreaskarzinom, welches auf eine initiale mindestens 4-6-monatige Systemtherapie nicht progredient ist, eine konventionell fraktionierte Radiotherapie, begleitet von einer Mono-Chemotherapie, angeboten werden.
Hammel et al., 2016 (LAP-07), Loehrer et al, 2011 (ECOG 4201), Chen et al, 2013, Metaanalyse


Kombinierte Radiochemotherapie Adjuvant: (Im Einzelfall diskutable Indikation)
Eine adjuvante Radiochemotherapie kann bei hohem Lokalrezidiv-Risiko (R1) indiziert werden, falls mFOLFIRINOX nicht gegeben werden kann.
Morganti et al, 2014, Butturini et al, 2008

C21:
Bei Analkarzinomen stellt die Radiochemotherapie die einzige kurative Therapieoption dar und ist somit bei allen Tumoren >T1N0, modifiziert nach RTOG/ECOG-Protokoll, die Standardtherapie (Flam et al., JCO 1996). Diese ist einer alleinigen Radiotherapie überlegen (EORTC-trial, Bartelink et al. JCO 1997). Auch im Vergleich zu operativen Massnahmen ist die lokale Kontrolle mit Radiochemotherapie überlegen und auch bei fortgeschrittenen Stadien noch sehr hoch (Grabenbauer DisColRectum 2005). Somit ist für das Analkarzinom die Radiochemotherapie gemäss NCCN-Leitlinie die Standardtherapie.
Flam 1996, Bartelink 1997, Grabenbauer 2005


C34:
SBRT Radiotherapie bei NSCLC Stadium I-IIb (cN0):
Für das nicht-kleinzellige Lungenkarzinom im Stadium I und II ohne Lymphknotenbefall ist die stereotaktische Strahlentherapie für inoperable Patienten aufgrund der geringen Toxizität, der sehr hohen lokalen Kontrolle von über 90% und der kurzen Behandlungszeit die Therapie der Wahl.
NCCN guideline, Postmus PE et al. Ann Oncol 2017, Schneider BJ et al. JCO 2017, Guckenberger M et al. Radiother Oncol 2017, Videtic GMM et al. PRO 2017, Ball D et al. Lancet Oncol 2019


Radiotherapie bei NSCLC Stadium III:
Die simultane Radiochemotherapie ist gemäss der Metaanalyse von Aupérin et al. 2018 einer sequentiellen oder alleinigen Radiotherapie bezüglich des Gesamtüberlebens mit einer Hazard Ratio von 0.84 überlegen. Sie ist somit im Stadium III mit kurativer Intention gemäss NCCN- und ESMO-Leitlinie als der Standard für die Lokaltherapie anzusehen.
NCCN guideline, Postmus PE et al. Ann Oncol 2017, Auperin A et al. JCO 2010
Aufgrund der zusätzlichen Verbesserung des Gesamtüberlebens durch die Reduktion einer späteren Fernmetastasierung sowie einer Verbesserung der lokalen Tumorkontrolle sollte eine adjuvante Immuntherapie mit Durvalumab nach Abschluss der Radiochemotherapie erfolgen.
Antonia SJ et al. NEJM 2018


Radiotherapie bei SCLC limited disease:
- Beim SCLC im Stadium limited disease verbessert die kombinierte Radiochemotherapie gefolgt von einer PCI das Gesamtüberleben. Daher stellt dieses Behandlungskonzept den Behandlungsstandard dar.
S3 Leitlinie, NCCN guideline, Murray N et al. JCO 1993, Auperin A et al. NEJM 1999

Radiotherapie bei SCLC extensive disease:
- Beim SCLC im Stadium extensive disease verbessern die konsolidierende thorakale Radiotherapie und PCI das Gesamtüberleben bei Patienten, welche auf die palliative Systemtherapie angesprochen haben. (NCCN Guidelines)
- Bei guter PR konsolidierende thorakale RTx. (Slotman BJ et al. Lung Cancer 2017)
- Bei CR unter CTx und Atezolizumab kann auf die thorakale RTx verzichtet werden. (Horn 2018)
- Bei mediastinaler Oligoprogression thorakale Radiotherapie zur Verbesserung der lokalen Kontrolle. (Paz-Ares 2019)

C45:
Malignes Pleuramesotheliom:
Die adjuvante Radiotherapie des Mesothelioms nach Pleurektomie/ Dekortikation/extrapleurale Pneumektomie bei Stadium I-IIIA kann eine effektive Therapieoption zur Verbesserung der lokalen Kontrolle bei einer R1-Situation darstellen, bei Patienten mit einem ECOG ≤1, guter Lungenfunktion sowie keine Anwesenheit von extrathorakalen Läsionen, wenn in einem interdisziplinären Tumorboard die Indikation für eine Lokaltherapie zur Verbesserung der lokalen Tumorkontrolle gestellt wurde.
(IMPRINT JCO 2016, Rusch J Thorac Cardiovasc Surg 2001)

Die palliative Radiotherapie des Mesothelioms ist eine effektive Therapieoption bei Schmerzen, bronchiale/oesophageale Obstruktion oder extrathorakale Metastasen.
NCCN Guidelines, ASCO Guidelines, SYSTEMS-1 Trial, Macleod Lung Cancer 2015

Die stereotaktische Radiotherapie des Mesothelioms kann bei Oligorecurrence oder Oligoprogression eine effektive Massnahme darstellen, wenn in einem interdisziplinären Tumorboard die Indikation für eine Lokaltherapie zur Verbesserung des progressionsfreien Überlebens sowie der lokalen Tumorkontrolle gestellt wurde.
Schröder Front Oncol 2019



C54.1:
Endometriumkarzinom - Postoperative Radiotherapie:

All risk groups:
ESGO/ESTRO/ESP Guidelines. Int J Gynecol Cancer 2021
ESGO/ESTRO/ESP guidelines for the management of patients with endometrial carcinoma (bmj.com)
ESMO/ESGO/ESTRO Guidelines. Int J Gynecol Cancer 2016
https://ijgc.bmj.com/content/ijgc/26/1/2.full.pdf
S3 Leitlinie 2018
https://www.leitlinienprogramm-onkologie.de/leitlinien/endometriumkarzinom/
NCCN Guidelines. V 1.2021
https://www.nccn.org/professionals/physician_gls/pdf/uterine.pdf

Low risk
Sorbe B, et al. Int J Gynecol Cancer 19:873-8;2009
https://ijgc.bmj.com/content/19/5/873-878.long
Klopp, et al Pract Radiat Oncol 4(3):
https://www.ncbi.nlm.nih.gov/pubmed/24766678

Intermediate risk
Creutzberg C, et al. PORTEC-1. IJROBP 2011
https://www.sciencedirect.com/science/article/pii/S036030161100530X?via%3Dihub
Nout R, et al. PORTEC 2. The Lancet 2010
https://reader.elsevier.com/reader/sd/pii/S0140673609621632?token=69202F9E8FC95B516BCA95D943CC87D92F40756A55EDD05C2039C42D541D5432CE607D203D927F16ABB8CAAAC8DC9ED8&originRegion=eu-west-1&originCreation=20210503135437
Sorbe BG, et al. “Norwegian” RND trial
https://pubmed.ncbi.nlm.nih.gov/22864336/
Wortman, et al. 10-year results PORTEC 2. BJC 2018
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6219495/pdf/41416_2018_Article_310.pdf
Kong A, et al. Metaanalysis. JNCI 2012
https://academic.oup.com/jnci/article/104/21/1625/952113

High Risk
De Boer S, et al.
PORTEC 3. The Lancet Oncology 2018
https://www.sciencedirect.com/science/article/pii/S1470204518300792?via%3Dihub
Emons G, et al. AGO Stellungnahme 2018
https://www.thieme-connect.com/products/ejournals/pdf/10.1055/a-0658-1918.pdf


C53:
Cervixkarzinom EBRT:

BIS STADIUM IB2: AUSWAHL TÄTIGEN:

Surgery vs. EBRT + conventional BT: 
Randomized phase 3 trial: no significant difference in OS, DFS & morbidity between EBRT without chemotherapy + conventional BT versus surgery for stage IB-IIA. Trend for inferiority of RT in adenocarcinoma. Morbidity worst after surgery and postoperative radiotherapy.
(Randomized study between radical surgery and radiotherapy for the treatment of stage IB–IIA cervical cancer: 20-year update (nih.gov))

Concomitant ChT:
Meta-analysis of individual patient data, 18 randomized trials: Addition of ChT to EBRT + conventional BT offers a modest, but significant benefit on OS, DFS, LR-DFS, M, and time to locoregional recurrence/progression. Effect in all stages with a trend for a higher benefit in 1A-IIA. Positive impact on time to metastases was smaller.
Reducing Uncertainties About the Effects of Chemoradiotherapy for Cervical Cancer: A Systematic Review and Meta-Analysis of Individual Patient Data From 18 Randomized Trials | Journal of Clinical Oncology (ascopubs.org)


ChRT + IGABT: 
retroEMBRACE stage I study: ChRT + IGABT in T1b1, T1b2 leads to excellent 5-year LC (98%), PC (96%), CSS (90%) & OS (83%) with limited morbidity and can be regarded equivalent to modern surgical techniques in terms of oncologic outcome.
Results of image guided brachytherapy for stage IB cervical cancer in the RetroEMBRACE
    
Consensus statement on surgery vs. RT: 
National Institute of Health: “stages IB-IIA are appropriately treated with equal effectiveness by either surgery or RT, but not both, to avoid increased cost and morbidity.”
National Institutes of Health Consensus Development Conference Statement on Cervical Cancer - ScienceDirect


AB STADIUM IB3: AUSWAHL TÄTIGEN:
ChRT + IGABT: 
EMBRACE 1 study of ChRT + IGABT: excellent 5-y LC (92%), PC (87%), DFS (68%) & OS (74%), limited morbidity (all stages). Stage IVA/B: LC 91%/89%, PC 81%/81%, OS 52%/61%.
MRI-guided adaptive brachytherapy in locally advanced cervical cancer (EMBRACE-I): a multicentre prospective cohort study - ScienceDirect

ChRT + IGABT: 
retroEMBRACE study of ChRT + IGABT: excellent 3-y LC (91%), PC (87%) and OS (74%), limited morbidity (all stages).
Image guided brachytherapy in locally advanced cervical cancer: Improved pelvic control and survival in RetroEMBRACE, a multicenter cohort study - ScienceDirect

Concomitant ChT: 
Meta-analysis; individual patient data from 18 randomized trials. Adding ChT to EBRT + conventional BT → a modest, but significant, benefit on OS, DFS, LR-DFS, MFS & time to locoregional recurrence/progression. Effect in all stages with a trend for a decrease with increasing stage. Positive impact on time to metastases smaller.
Reducing Uncertainties About the Effects of Chemoradiotherapy for Cervical Cancer: A Systematic Review and Meta-Analysis of Individual Patient Data From 18 Randomized Trials | Journal of Clinical Oncology (ascopubs.org)

Adjuvant ChT: 
Meta-analysis; individual patient data from 18 randomized trials: no benefit of adding adjuvant ChT to EBRT + conventional BT. OUTBACK trial: negative.

Neoadjuvant ChT + surgery versus ChRT + IGABT: 
Randomized phase 3 trial: ChRT + conventional BT superior to neoadjuvant ChT + surgery (stage IB3-IIB) in terms of higher DFS. OS not significantly different. INTERLACE Study protocol should not be considered standard in unselected patients. Selection criteria for eventual NACT not established.
Neoadjuvant Chemotherapy Followed by Radical Surgery Versus Concomitant Chemotherapy and Radiotherapy in Patients With Stage IB2, IIA, or IIB Squamous Cervical Cancer: A Randomized Controlled Trial | Journal of Clinical Oncology (ascopubs.org)


AUSWAHL TÄTIGEN:
STANDARD PROCEDURE: IB3 & IIA2
ChRT + IGABT preferred to avoid surgery + adjuvant therapy. Neoadjuvant ChT + surgery not recommended. NACT plus radiotherapy not recommended for unselected patients; can be considered on individualized-concept basis by tumour-board.
(ESGO Guidelines, Lindegaard JC, Petric P, Tan LT, Hoskin P, Schmid MP, et al. Are we making progress in curing advanced cervical cancer-again? Int J Gynecol)

STANDARD PROCEDURE: IIB-IVA
ChRT + IGABT recommended. Neoadjuvant chemotherapy + surgery not recommended. NACT plus radiotherapy not recommended for unselected patients; can be considered on individualized-concept basis by tumour-board. N+: SIBEBRT to involved N.
(ESGO Guidelines, Lindegaard JC, Petric P, Tan LT, Hoskin P, Schmid MP, et al. Are we making progress in curing advanced cervical cancer-again? Int J Gynecol)

c51:
Vulvakarzinom - Postoperative Radiotherapie:

Indications for RT to the vulva:
Post-operative radiotherapy to the vulva is recommended for all women with a positive margin where re-excision is not possible. Radiotherapy may also be considered in the setting of risk factors for local recurrence: close margins, lymphovascular or perineural invasion, large tumor size, and/or depth of invasion >5 mm. ESGO Guidelines 2023
    
Patients with vulvar squamous cell carcinoma and positive surgical mar gins derive an OS benefit from aRTwith a seemingly optimal dose in the range of 54.0 to 59.9 Gy. 2016 Chapman BV, et al. IJROBP 2017

Adjuvant RT should be used for patients with positive/close surgical margins to improve their outcome. Ignatov T, et al. J Cancer Clin Res 2016


Indication for postoperative inguino/femoral/pelvic radiotherapy:
Database study of 2779 patients (1436 1N+, 1208 with ≥2 N+) showed better survival for adjuvant chemoradiotherapy compared with radiotherapy in patients with 1 and those with 2 or more positive nodes. 
5-year overall survival was highest among patients with one positive node who received chemoradiotherapy (68.1%), compared with 55.9% for adjuvant external beam radiation therapy and 46.1% for no adjuvant treatment. 
Survival was likewise highest among patients with two or more positive nodes who received chemoradiotherapy (49.1%), compared with 29.4% for adjuvant external beam radiation therapy and 21.2% for no adjuvant treatment. 
However, in this analysis women with a single positive node derived a survival advantage from radiotherapy but no incremental advantage from the addition of chemotherapy to radiotherapy. 
Rydzewski NR, et al. Role of adjuvant external beam radiotherapy and chemotherapy in one versus two or more node-positive vulvar cancer: A National Cancer Database study. Radiother Oncol. 2018 Dec;129(3):534-539.


Indication for including local irradiation of vulva to the inguino/femoral/pelvic radiotherapy:
Large retrospective AGO-CaRE −1 study on pN+ vulvar cancer showed that adjuvant radiation to the primary site in addition to the groins/pelvis lymph nodes results in less vulva-only recurrences (15.8%) as compared with 22.8% in patients with adjuvant radiotherapy to groins/pelvis and 25.5% with no adjuvant radiotherapy. The risk-reducing effect of local radiotherapy was independent of the resection margin status. There was greater impact of RT for HPV-related than -independent tumours with median disease-free survival of 20.7 versus 17.8 months, respectively. Woelber L, et al. Gynecol Oncol. 2022 Jan;164(1):68-75.


Indications for RT to the groins instead of lymphadenectomy
• Consider in SLN+ (≤2 mm) instead of lymphadenectomy
Patients with SLN metastasis ≤2 mm can be treated with postoperative radiotherapy (2-year isolated groin recurrence rate of 1.6% in GROINSS-V II), as a safe alternative to inguinofemoral lymphadenectomy. Patients with early-stage vulvar cancer with SLN metastasis >2 mm following SLN biopsy should undergo inguinofemoral lymphadenectomy followed by post-operative radiotherapy in case of one or more additional lymph node metastasis and/or extracapsular tumor spread; the 2-year isolated groin recurrence rate was unacceptably high (22%) with radiotherapy alone using 50 Gy in the GROINSS-V II study (Oonk MHM, Slomovitz B, Baldwin PJW, et al. Radiotherapy versus inguinofemoral lymphadenectomy as treatment for vulvar cancer patients with micrometastases in the sentinel node: results of GROINSS-V II. J Clin Oncol 2021;39:3623–32. Lukovic J, Han K. Postoperative management of vulvar cancer. Int J Gynecol Cancer 2022;32:338–43.)

Indications for Concomitant Chemotherapy:
Retrospective studies suggest that the addition of concurrent chemotherapy to radiotherapy may improve survival. Toxicity of radiotherapy versus chemoradiotherapy in this situation needs to be carefully considered on an individual patient basis. Lukovic J, Han K. Postoperative management of vulvar cancer. Int J Gynecol Cancer. 2022.
Database study of 2779 patients (1436 1N+, 1208 with ≥2 N+) showed better survival for adjuvant chemoradiotherapy compared with radiotherapy in patients with 1 and those with 2 or more positive nodes. 5-year overall survival was highest among patients with one positive node who received chemoradiotherapy (68.1%), compared with 55.9% for adjuvant external beam radiation therapy and 46.1% for no adjuvant treatment. Survival was likewise highest among patients with two or more positive nodes who received chemoradiotherapy (49.1%), compared with 29.4% for adjuvant external beam radiation therapy and 21.2% for no adjuvant treatment. However, in this analysis women with a single positive node derived a survival advantage from radiotherapy but no incremental advantage from the addition of chemotherapy to radiotherapy. Rydzewski NR, et al. Role of adjuvant external beam radiotherapy and chemotherapy in one versus two or more node-positive vulvar cancer: A National Cancer Database study. Radiother Oncol. 2018 Dec;129(3):534-539.
In a large population-based analysis, adjuvant chemotherapy resulted in a significant reduction in mortality risk for node-positive vulvar cancer patients who received adjuvant radiotherapy. Gill BS, et al. Impact of adjuvant chemotherapy with radiation for node-positive vulvar cancer: A National Cancer Data Base (NCDB) analysis. Gynecol Oncol. 2015.


C83.3:
Die lokale Radiatio nach durchgeführter Chemotherapie bei DLBCL mit initialem Bulk oder residual mass > 2 cm verbessert die lokale Kontrolle, das progressionsfreie Überleben und das Gesamtüberleben bei Patienten mit DLBCL.
ESMO guideline DLBCL 2015, NCCN B-Cell Lymphomas 2020, Pfreundschuh et al JCO 2018

Bei initialem ossären Befall sollte die RT evaluiert werden wenn ein unifocaler Befall oder ein bulky disease vorliegt, Weichgewebe (soft tissue) mit eingeschlossen war und ein unklares Ansprechen vorliegt
Held JCO 2013, Freeman Blood 2021


C81.9:
Die lokale Radiatio bei M Hodgkin verbessert die lokale Kontrolle und konsekutiv das progressionsfreie Überleben und das Gesamtüberleben bei Patienten mit Morbus Hodgkin. Stadienabhängig und nach Ansprechen im PET-CT erfolgt die Indikationsstellung und Dosierung.
Eich et al 2018, S3 Leitlinie M Hodgkin Oktober 2022

C88.4:
MALT Lymphome können im Frühstadium (im Stadium IA und IIA) mit alleiniger Radiatio geheilt werden. Bei Befall des Magens sollte immer eine vorherige Eradikation von Helicobacter pylori durchgeführt werden, bei mehr als der Hälfte der Patienten führt dies bereits zu einer langfristigen Lymphomkontrolle.
Hoskin P et al Lancet Oncol 2021 Mar

C90.00:
Radiotherapy treatment is the treatment of choice for Solitary Plasmozytoma with high local control rates and long-term curation.
Yahalom J et al Int J Radiation Oncol Biol Phys 2018, Elsayad K et al Strahlenther Onkol 2020 Feb


C50:


Radiotherapie der Mamma nach BET:
Die postoperative Bestrahlung der Mamma senkt das Risiko für ein Lokalrezidiv und Fernmetastasen signifikant (RR 0.52). Zusätzlich ist in einer Meta-Analyse mit über 10.000 Patientinnen eine signifikante Verbesserung des Überlebens durch die adjuvante Radiotherapie nachgewiesen (RR 0.82). Dabei ist die hypofraktionierte Radiatio der normofraktionierten Radiotherapie ebenbürtig.
EBCTCG – Metaanalyse, Darby et al, Lancet 2011; 378: 1707–16, 10 year results, START A + B, Haviland et al, Lancet Oncol 2013; 14: 1086–94
Eine zusätzliche Aufsättigung des Tumorbetts (Boost) senkt das Lokalrezidivrisiko zusätzlich in allen Patientinnen-Subgruppen (HR 0.65).
EORTC Boost vs no boost trial,Bartelink et al, Lancet Oncol 2015; 16: 47-56, French Boost trial, Romestaing et al. JCO, 1997. 15(3): 963-968
Somit ist die postoperative hypofraktionierte Radiotherapie der Mamma inklusive Boost-Bestrahlung Standardtherapie.
S3 –Leitlinie : Seite 140 - 145

Radiotherapie des Lymphabfluss:
Die zusätzliche Radiotherapie der Lymphabflussgebiete zeigt bei Patientinnen mit mehr als 3 befallenen Lymphknoten oder Vorliegen von Risikofaktoren einen signifikanten Vorteil bezüglich Überleben mit einer Hazard ratio von 0.87 in einer prospektiv randomisierten Studie (Poortmans et al,NEJM 2015).
EORTC 22922 10925, Poortmans et al, NEJM, 2015;373:317-27, MA.20 study, Whelan et al, NEJM 2015;373:307-16, Dänische Kohortenstudie DBCG – IMN, Thorsen et al, JCO 2016; 34:314-320, French-Trial, Hennequin et al, IJROBP 2013; 86: 860-866, Metaanalyse, Budach et al, Radiat Oncol 2015; 21;10:258

RT Teilbrust nach ipsilateraler Vorbelastung:
Nach erneuter brusterhaltender Operation eines Mammakarzinoms ist die postoperative Radiotherapie der Mamma erneut möglich.
RTOG 1014 Phase II Clinical Trial Effectiveness of breast conserving surgery and partial breast reirradiation for recurrence of breast cancer in the ipsilateral breast https://pubmed.ncbi.nlm.nih.gov/31750868/
Local recurrence of breast cancer: conventionally fractionated partial external beam re-irradiation with curative intention - PubMed (nih.gov) Janssen et al Strahlenther Onkol 2018 sep
NRG Oncology–Radiation Therapy Oncology Group Study 1014: 1-Year Toxicity Report From a Phase 2 Study of Repeat Breast-Preserving Surgery and 3-Dimensional Conformal Partial-Breast Reirradiation for In-Breast Recurrence – IJROBP 2017 vol 98

Radiotherapie der Thoraxwand nach Mastektomie (PMRT):
Die Bestrahlung der Brustwand nach Mastektomie ist bei Patientinnen mit lokal fortgeschrittenem und/oder nodal-positivem Mammakarzinomen mit einer Reduktion der Lokoregionären- sowie Fernrezidive (RR 0.75) und der Reduktion der brustkrebs-spezifischen Sterblichkeit (0.84) assoziiert. Dies konnte in einer grossen Metaanalyse mit über 8.000 Patientinnen nachgewiesen werden.
EBCTCG Metaanalyse, Darby et al, Lancet 2014; 383: 2127–35
Somit ist die postoperative Radiotherapie der Thoraxwand und Lymphabflusswege gemäss S3 Leitlinie Standardtherapie.
S3 –Leitlinie : Seite 147 - 151

Radiotherapie der Mamma bei DCIS:
Die Postoperative Bestrahlung der Mamma senkt das Risiko für ein Lokalrezidiv nach Resektion eines DCIS signifikant. So zeigten randomisierte Studien mit über 4000 Patientinnen, dass sich nach Radiatio das Lokalrezidivrisiko um mehr als die Hälfte senken lässt.
EBCTCG review, Correa et al, J Natl Canc Inst 2010; 2010(41):162-77
Somit ist die postoperative Radiotherapie der Mamma gemäss S3 Leitlinie Standardtherapie.
S3 –Leitlinie : Seite 83-84

Partial Breast RT Mamma:
Nach brusterhaltender Operation eines Mammakarzinoms ist die postoperative Radiotherapie der Mamma und bei Befall der Lymphknoten auch des LAG eine etablierte kurative Therapie. In Niedrigrisiko-Situationen kann dies auch als Teilbrustbestrahlung durchgeführt werden.
(NCCN 2/2016; Sautter-Bihl ML Strahlenther Onkol 2014, Sedlmayer F Strahlenther Onkol 2013, Whelan et al)
-Partial breast irradiation after breast concervation surgery for patients withearly breast cancer ( UK IMPORT LOW trial) 5-years results from a multicenter,randomized, controlled, phase 3 non-inferiarity trial (Coles et al, Lancet 2017,August, abstract LBA 10 - 10 years results ASTRO 2023)
-Accelerated partial-breast irradiation compared with WBRT for early breastcancer: Long term results of the randomized phase III APBI-IMRT Florence trial( Meattini et al JCO 2020 Vol 38, Number 35)
-Hypofractionated breast radiotherapy for 1 week versus 3 weeks FASTFORWARD: 5 year efficacy and late normal tissue effects results from amulticenter, non-inferiority randomised phase 3 trial (Brunt et al Lancet 2020;395:1613-26)


C44:

Rechtfertigende Indikation für die definitive Radiotherapie:
Grundsätzlich ist die definitive Radiotherapie des BCC/cSCC als primärkurative Behandlungsmodalität bei allen Patienten empfohlen, bei denen eine operative Resektion des Tumors im Gesunden nicht möglich ist oder vom Patienten abgelehnt wird. 
Eine Meta-Analyse von Drucker et al. in 2018 fand ähnlich gute Lokalkontrollraten zwischen primär resezierten und primär bestrahlten Tumoren. Bei Patienten mit BCC oder cSCC in Lokalisationen, in denen eine Resektion des Tumors zu relevanten funktionellen oder kosmetischen Einbussen führt, ist daher die definitive Radiotherapie als Alternative zur Resektion ebenfalls empfohlen. CAVE: Eine Strahlentherapie sollte bei Patienten mit Syndromen und Autoimmunerkrankungen, die mit erhöhter Strahlenempfindlichkeit einhergehen, nicht angewandt werden (z.B. Basalzellkarzinomsyndrom, Xeroderma pigmentosum, Lupus erythematodes, Sklerodermie).
ASTRO Clinical Practice Guideline (2020), Drucker et al., Ann Intern Med.(2018)



Rechtfertigende Indikation für die postoperative Radiotherapie

--> der ehemaligen Primärtumorregion:
Die postoperative Radiotherapie (PORT) hat sich als
Behandlungsmodalität für Patienten mit BCC/cSCC etabliert, bei denen
aufgrund ungünstiger, tumorspezifischer Faktoren ein erhöhtes Risiko
für ein Lokalrezidiv besteht. Insgesamt ist das cSCC eine aggressivere
Tumorentität als das BCC, weswegen für Patienten mit cSCC ein
breiteres Spektrum anerkannter Risikofaktoren existiert, die eine
postoperative Radiotherapie indizieren.
Brantsch et al., Lancet Oncol. (2008), Sapir et al., Radiother Oncol. (2016)

-->des (elektiven) Lymphabflussgebiets bei SCC:
Die Behandlungsbedürftigkeit des lokoregionären Lymphabflussgebiets richtet sich nach dem Vorhandensein einer klinisch oder radiologisch vorliegenden Lymphknotenmetastasierung, unter Einbezug des Risikos für einen subklinischen Lymphknotenbefall. Patienten mit klinisch oder radiologisch erkennbarer Lymphknotenmetastasierung sollten primär einer therapeutischen Lymphadenektomie unterzogen werden, es sei denn, es liegt eine Inoperabilität des Patienten oder Irresektabilität des Befundes vor. Grundsätzlich besteht die Indikation für eine PORT des (elektiven) LAG bei:
- pN+ (Ausnahme: singuläre Lymphknotenmetastase < 3 cm ohne ECE)
- cN+ (falls Pat. inoperabel/LK-Metastasen irresektabel)
ASTRO Clinical Practice Guideline (2020), Ebrahimi et al., Head Neck. (2012)

Konkomitierende Systemtherapie (cSCC):
In Abwesenheit eines klar belegbaren Zusatznutzens ist der Einsatz einer simultanen, platinhaltigen Chemotherapie konkomitierend zur Radiotherapie von lokal fortgeschrittenen cSCCs weder im definitiven, noch im adjuvanten Setting empfohlen. Dies gilt insbesondere auch in Anbetracht des höheren Durchschnittsalters und der häufigen Immunsuppression/Komorbiditäten des Patientenkollektivs.
Porceddu et al., J Clin Oncol. (2018)


C43:

[AKTUALISIERTE SOP NOCH NICHT AUF RAO_DATEN HOCHGELADEN (Stand 02.07.2025), WORK IN PROGRESS]

C4A.9:
Radiotherapie bei Merkelzellkarzinom (MCC)
Eine postoperative Radiotherapie führt zur besserem progressionsfreiem Überleben (HR 0.45, 95% CI: 0.32-0.62) und Gesamtüberleben (HR 0.81, 95%CI 0.75-0.86). 
Deswegen sollte eine adjuvante Radiotherapie nach jeder Primärresektion durchgeführt werden, auch bei R0-Resektion und für kleine Tumoren. Bei ausschliesslich positiven prognostischen Faktoren wie Tumordiameter ≤ 1cm, keine lymphatische Invasion, Lokalisation ausserhalb des Kopf-Hals-Bereichs, Resektionsränder ≥ 1cm sowie Immunkompetenz, kann ein Verzicht auf eine Radiotherapie des Tumorbetts erwogen werden.
Becker et al. - Journal of the German Society of Dermatology 2018, Petrelli et al., Radiother Oncol, 2019, Mojica et al., J Clin Oncol, 2007

Eine RT-Indikation besteht ausserdem bei Patienten mit positivem/knappem Resektionsrand, bei inoperablen Patienten, zur Palliation oder bei makroskopischen nicht-operierten Lymphknoten.
Ligowska et al, ESMO Guidelines, 2024; Veness et al., Int J Radiat Oncol Biol Phys, 2010

Bei fortgeschrittenen Merkelzellkazinomen, welche nicht mehr kurativ mittels Operation oder Radiotherapie behandelt werden können, ist die Gabe einer Immuntherapie mit PD-1/PD-L1 Blockern die Therapie der Wahl.
Gulley et al. - The Lancet Oncology 2017, Ligowska et al, ESMO Guidelines 2024

Oligometastasierung-Oligoprogression unter Immuntherapie:
Die Kombination von Immuntherapie mit Avelumab und Radiotherapie wird gerechtfertigt durch Fallberichte und die theoretischen synergistischen Effekte, die zur Optimierung der Behandlungsergebnisse führen. Avelumab erhöht die Radiosensibilität des Tumors, was zu einer verbesserten lokoregionalen Kontrolle beiträgt. Gleichzeitig induziert die Radiotherapie eine Immunsensibilisierung, die eine verstärkte systemische Tumorkontrolle ermöglicht. Die in der Literatur dokumentierten positiven Ergebnisse bei der simultanen Anwendung beider Therapien unterstützen die Anwendung dieser Strategie beim Merkelzellkarzinom, um das Therapieergebnis zu maximieren.
Principe et al. BMJ Case Rep. 2019, Sharabi et al. Lancet Oncol. 2015


D32: 
Rechtfertigende Indikation:
Die Indikationsstellung zur Strahlentherapie von WHO Grad I, II und III Meningeomen erfolgt gemäss den Empfehlungen der Leitlinien Neuroonkologie des Klinischen Neurozentrums USZ.


C71:
Radiotherapie bei hochgradigen Gliomen:


Anaplastisches Astrozytom:
Die EORTC Studie 26053-22054 zeigte, dass die Strahlentherapie gefolgt von einer adjuvanten Temozolomid-Chemotherapie mit einem signifikanten Überlebensvorteil bei Patienten mit neu diagnostizierten nicht-ko-deletierten anaplastischen Gliomen assoziiert ist. Somit ist die alleinige postoperative Strahlentherapie mit kumulativ 60 Gy gefolgt von 12 Zyklen Temodal gemäss NCCN und ESMO Leitlinie als Standard anzusehen (Van den Bent et al, Lancet. 2017 Oct 7;390(10103):1645-1653)



Glioblastom:

Kombinierte Radiochemotherapie:
Die Zugabe von Temozolomid zu einer normo-fraktionierten Strahlentherapie bei neu diagnostiziertem Glioblastom führte zu einem klinisch bedeutsamen und statistisch signifikanten Überlebensvorteil bei einer Hazard Ratio von 0.63 mit minimaler zusätzlicher Toxizität.
Somit ist die postoperative Radiochemotherapie, gefolgt von einer adjuvanten Temodaltherapie, gemäss NCCN und ESMO Leitlinie die Standard-Behandlung.
(Stupp et al. New England Journal of Medicine 2005)

Radiochemotherapie bei elderly Patienten:
Die Zugabe von Temozolomid zu einer hypo-fraktionierten Strahlentherapie bei neu diagnostiziertem
Glioblastom von Patienten älter als 65 Jahren führte zu einem klinisch bedeutsamen und statistisch
signifikanten Überlebensvorteil bei einer Hazard Ratio von 0.67 mit minimaler zusätzlicher Toxizität.
Somit ist die hypo-fraktionierte Radiochemotherapie, gefolgt von einer adjuvanten Temodaltherapie, insbesondere bei Patienten mit MGMT-Methylierung und gutem Performance-Status als Therapie der Wahl anzusehen.
(Perry et al. New England Journal of Medicine 2017)

TMZ oder RT bei elderly Patienten:
Basierend auf dem systematischen Review von Zarnett et al., ist die alleinige hypofraktionierte Strahlentherapie eine Standard-Behandlung von älteren Patienten mit neu diagnostiziertem GBM, bei welchen eine Kombinationstherapie aus hypo-fraktionierter Strahlentherapie und Temodal nicht möglich ist.
(Zarnett et al. JAMA Neurol. 2015)

C79.3:

Primäre Radiochirurgie:
Die EORTC 22952-26001 Studie, welche die Wertigkeit einer alleinigen Radiochirurgie ohne Ganzhirnbestrahlung zur Behandlung einer limitierten Hirnmetastasierung untersuchte, ergab ein gleichwertiges Gesamtüberleben bei sehr guter lokaler Kontrolle der therapierten Metastasen (Kocher et al., JCO, 2011).
Daher ist die Radiochirurgie bei limitierter Hirnmetastasierung als Standardtherapie anzusehen.
Die Radiochirurgie ist daher auch bei multiplen Hirnmetastasen (n<10) als Standard einer Ganzhirnbestrahlung vorzuziehen. Bei mehr als 10 Hirnmetastasen kann die Radiochirurgie bei guter technischer Durchführbarkeit ebenfalls in Erwägung gezogen werden, um die neurokognitiven Folgen einer Ganzhirnbestrahlung zu vermeiden. (Yamamoto et al., Lancet Oncology, 2014)

Additive postoperative Radiotherapie:
Die NCCTG N107C Studie zeigte, dass nach Resektion von Hirnmetastasen eine fraktionierte stereotaktische Radiotherapie der Resektionshöhle der Ganzhirnbestrahlung bezüglich des Gesamtüberlebens gleichwertig ist. Die Neurokognition war nach stereotaktischer Radiotherapie mit einer Hazard Ratio von 0.47 signifikant besser erhalten als nach Ganzhirnbestrahlung (Brown et al., Lancet Oncology, 2017).
Daher ist die Radiochirurgie nach Metastasenresektion bei limitierter Hirnmetastasierung als Standard anzusehen und es kann auf eine Ganzhirnbestrahlung verzichtet werden.


D33.3:
Bei wachsendem, symptomatischem Vestibularisschwannom nach initialer Observation ist entweder eine stereotaktische Radiochirurgie (SRS) oder eine fraktionierte stereotaktische Radiotherapie (SRT) eine etabilierte kurative Therapieoption.

C11:
Primärsituation:

Rechtfertigende Indikation lokal begrenztes NPC (Stadium I, II):
Stadium I: Alleinige RT, keine belastbare Evidenz für zusätzlichen Nutzen durch Chemotherapie im Stadium I
Stadium II keine und bei frühem Stadium III (T3 N0 M0) kritische Prüfung einer simultanen Chemotherapie, mittlerweile eher eine alleinige RT bevorzugt
Eine Phase III Studie, die 341 Patienten mit Stadium II und III (T3 N0 M0) NPC zwischen RT und RCT randomisierte, zeigte eine Non-inferiority und weniger Toxizität der alleinigen Bestrahlung.
Chan et al., Annals of Oncology 23 (Supplement 7): vii83–vii85, 2012 –ESMO guideline, Chen et al., J Natl Cancer Inst 2011

Rechtfertigende Indikation lokal fortgeschrittenes NPC (Stadien III mit N1/N2-IVa):
Eine grosse Meta-Analyse von 20 prospektiven Studien und über 5,000 Patienten untersuchte den Einsatz der Strahlentherapie kombiniert mit Chemotherapie-Applikation bei Patienten mit lokal fortgeschrittenem Nasopharynxkarzinom.
Ling-Long Tang et al., JAMA Network, 2022
Die Platin-basierte Chemotherapie vor oder nach einer simultanen Radiochemotherapie, sowie die alleinige simultane Radiochemotherapie waren mit einem statistisch signifikanten Überlebensvorteil für diese Patienten assoziiert, verglichen mit alleiniger Bestrahlung. Die entsprechenden HRs waren für adjuvante CT+CRT 0.65, für CRT 0.77, und für Induktions-CT+CRT 0.81. Dabei konnten für die adjuvante CT+CRT verglichen mit CRT ein signifikanter Vorteil bzgl. progressionsfreiem Überleben (HR 0.81) und für die Induktions-CT+CRT ein Vorteil verglichen mit CRT bzgl. Fernmetastasierung (HR 1.55) gezeigt werden. Die Zugabe von Cisplatin simultan zu einer Strahlentherapie bis 70 Gy bei neu diagnostizierten Nasopharynxkarzinomen führte zu einem klinisch bedeutsamen und statistisch signifikanten Überlebensvorteil bereits in der Intergroup-Studie 0099 (bei einer Hazard Ratio von alleiniger Radiotherapie zur simultanen Radiochemotherapie von 3.28 nach 3 Jahren).
Ribassin-Majed et al. J Clin Oncol. 2017 Fe 10;35(5):498-505.
Al-Sarraf et al JCO 1998 16(4):1310-7
Alternative (Platin non-eligible):
Als «platin non-eligible» werden Patienten mit GFR < 55ml/min oder EF < 50% oder fortgeschrittener Schwerhörigkeit (z.B. Hörgerät-Versorgung) oder mehreren der folgenden Faktoren eingestuft: Alter >70 J, leichte Schwerhörigkeit, Polyneuropathie, schwere Komorbidität (nicht gut eingestellter Diabetes, HIV mit Viruslastnachweis usw.).
Bei Patienten mit ECOG 0-1 und nur leicht reduzierter Nierenfunktion (GFR > 40ml/min) oder nur fortgeschrittener Schwerhörigkeit wäre auch Carboplatin/5-FU als individuelles Procedere möglich.

Rechtfertigende Indikation metastasiertes NPC (Stadium IVb):
Patienten mit einem primär metastasierten NPC (mNPC) sollten nach neoadjuvanter CTx mit Cisplatin/5-FU eine RCT erhalten.
Eine Phase III Studie untersuchte 173 Patienten mit mNPC, die eine neoadjuvante CTx mit Cisplatin/5-FU erhielten und anschliessend randomisiert wurden in CTx alleine versus RCT. Patienten im RCT-Arm zeigten eine statistisch signifikant verbessertes Gesamtüberleben (HR 0.42, p=0.004); höhergradige Spättoxizitäten waren <10%.
You et al, JAMA Oncology, 2020




Rezidivsituation:

Rechtfertigende Indikation bei Lokalrezidiv:
Die sich etablierende Standardtherapie bei Lokalrezidiv ist die Operation.
Eine Phase III Studie untersuchte bei der 200 Patienten mit Lokalrezidiv eines NPC die Behandlung mit endoskopischer Resektion versus Bestrahlung mit IMRT. Es konnte gezeigt werden, dass operierte Patienten ein signifikant besseres Gesamtüberleben nach 3 Jahren haben als die bestrahlten Patienten (HR: 0.47, 95% CI 0.29–0.76; p=0.0015). Die Operation ging ausserdem mit einem besseren Sicherheits- und Toxizitätsprofil einher: Während 5/99 (5%) operierte Patienten an Behandlungs-assoziierten Nebenwirkungen starben, waren dies 20/101 (26%) in der IMRT-Gruppe.
Bei lokal oder allgemein inoperablen Patienten oder R1-Situationen, ist eine Re-Bestrahlung indiziert.
You-Ping Liu et al., The Lancet Oncology 2021, Wai Tong Ng et al. IJRBP, 2021
Eine Phase III Studie randomisierte 178 Patienten mit NPV-Lokalrezidiv (T2-T4; N1-N2) zwischen Hyperfraktionierung (65 Gy / 54 Fx; di-daily; >6 Std. Gap) versus Normo-fraktionierung (60 Gy / 27 Fx). Es konnte gezeigt werden, dass die Patienten in der Hyperfraktionierung im Vergleich zur Normofraktionierung Subgruppe ein besseres Gesamtüberleben nach 3 Jahren (HR für Tod: 0.54, 95% CI 0.33 to 0.88; p=0·014) sowie weniger Grad 5 Toxizität (7% vs. 16%) hatten.
Rui You et al., The Lancet, 2023


C32:
Primäre Radio(chemo)therapie Larynx- und Hypopharynxkarzinom:
Rechtfertigende Indikation T1 bis kleines T2 N0:
Die prospektiv-randomisierte DAHANCA 6/7- Studie untersuchte den Einsatz der Strahlentherapie mit 6 Fraktionen wöchentlich für Patienten mit lokal begrenzten Larynxkarzinomen. Insgesamt konnte mittels Radiotherapie mit 6 Fraktionen pro Woche bei der grossen Mehrheit der Patienten der Tumor kontrolliert und die Larynxfunktion erhalten werden.
Die definitive Strahlentherapie mit dem Ziel des Organerhalts für das neu diagnostizierte, lokal begrenzte Larynxkarzinom ist gemäss NCCN und ESMO Leitlinie als etablierte Option anzusehen.
Overgaard et al., Lancet. 2003 Sep 20;362(9388):933-40

Rechtfertigende Indikation lokal fortgeschrittenes Larynx-Ca:
Die prospektiv-randomisierte R91-11- Studie untersuchte den Einsatz der Strahlentherapie mit gleichzeitiger Cisplatin-basierter Chemotherapie für Patienten mit lokoregional fortgeschrittenen, potentiell operablen Larynxkarzinomen. Insgesamt konnte mittels simultaner Radiochemotherapie bei der grossen Mehrheit der Patienten der Kehlkopf erhalten bleiben. Die simultane Chemotherapie war mit einem klinisch und statistisch signifikanten Vorteil bzgl. Larynx-Erhalt verglichen mit alleiniger Bestrahlung (p<0.001) assoziiert.
Somit ist die definitive Strahlentherapie simultan zu Cisplatin mit dem Ziel des Organerhalts für das neu diagnostizierte Larynxkarzinom gemäss NCCN und ESMO Leitlinie als etablierte Option anzusehen.
Forastiere et al., N Engl J Med. 2003 Nov 27;349(22):2091-8.

FÜR ALLGEMEINGÜLTIGE, ADJUVANTE RCT BEI ORL-TUMOREN SIEHE ZUDEM 06_02_10_ORL-adjuvant _2019-10-30.pdf in RAO_Daten


C30:
Primäre kurative Therapie bei inoperablen Tumoren ist die Radio(chemo)therapie. Bei T1/T2 Tumoren auch alleinige RT.
- Organerhaltende Alternative zu ggf. mutilierender OP
- Postoperativ bei inkompletter Resektion oder knappem RR Rand

C10:

Radio(chemo)therapie bei Oropharynxkarzinom:
Lokoregionär begrenztes Oropharynxkarzinom (Stadien I und II: p16-positiv T1-T3N2; p16-negativ T1-T2N0):
Die primär nicht-operative Therapie bei Patienten mit HPV+/- OPSCC im Stadium T1-2 cN0 soll als alleinige Strahlentherapie erfolgen.
Bei Patienten mit Oropharynxkarzinomen in den Stadien I-II (UICC 8. Ausgabe) gibt es keine Hinweise, dass die Ergebnisse einer primär chirurgischen Therapie (+/- adjuvanter Radio-/ Radiochemotherapie) und einer primären Radio- /Radiochemotherapie sich signifikant in Bezug auf das Gesamtüberleben, das rückfallfreie Überleben, die lokoregionäre Rückfallfallrate und das fernmetastasenfreie Überleben unterscheiden.
S3-Leitlinie


Primäre Radio-(chemo-)therapie:
In einer randomisierten internationalen open-label Phase II Studie verglichen Nichols et al. bei Patienten mit T1/2 N0-2 oropharyngealen Plattenepithelkarzinomen (unabhängig vom HPV-Status) eine definitive R(CH für N+)T mit einer Tumorresektion (TORS) und Neck-Dissection. Sie konnten zeigen, dass die QoL nach 1 Jahr bzgl. Schluckfunktion (MDADI) nicht signifikant unterschiedlich war, bei gleichem OS (p = 0.89) und PFS (p = 0.63). Die Toxizitätsprofile waren unterschiedlich. Die R(CH)T mit 70Gy über 7 Wochen (und 100mg/m2KOF Cisplatin q3w) stellt eine gute Alternative zur Operation dar und sollte daher angeboten werden.
ORATOR-Studie Nichols et al Lancet Onc, 2019


Lokal fortgeschrittenes Oropharynxkarzinom (p16 positiv, St. III: T1N3 - T4; p16-negativ St. III und IV-A,-B: T3-TxN3, M0):
Bei OPSCC cN1-3 oder T3-4 sollte die primär nicht-operative Therapie als simultane Radiochemotherapie erfolgen.
Die grosse Meta-Analyse MACH-NC von über 16.000 Patienten untersuchte den Nutzen einer zusätzlichen, zur Radiotherapie konkomittierenden Chemotherapie bei Patienten mit meistens lokoregionär fortgeschrittenen Plattenepithelkarzinomen im Kopf-Hals Bereich (88% St. III-IV). Die simultane Platin-basierte Chemotherapie war mit einem signifikanten Überlebensvorteil bei diesen Patienten unabhängig von der genauen Tumorlokalisation assoziiert. Die Zugabe von Cisplatin simultan zu einer Strahlentherapie bei neu diagnostizierten Kopf-Hals Plattenepithelkarzinomen führte zu einem klinisch bedeutsamen und statistisch signifikanten Überlebensvorteil bei einer Hazard Ratio von 0.87-0.88 und einem 5-yr absoluten Benefit für Oropharynxkarzinomen vom 8.1%.
S3-Leitlinie, Blanchard et al., MACH-NC, Radiother Oncol. 2011



Adjuvante Radio-(chemo-)therapie:
Bei primär chirurgisch behandelten, HPV-positiven und negativen OPSCC im Stadium pT1-2 N0 und mit R0 oder Resektionsränder (RR) >5mm kann man auf eine adjuvante Radiotherapie verzichten.
Bei primär chirurgisch behandelten, HPV-positiven und negativen OPSCC im Stadium pT1-2 N1 mit nur einem befallenen Lymphknoten <3cm kann man auf eine adjuvante Radiotherapie verzichten, falls alle von diesen Kriterien erfüllt sind:
● G1-2 (bei HPV-)
● L0
● V0
● Pn0
● R0
Bei primär chirurgisch behandelten OPSCC sollte eine adjuvante Radio-(chemo)therapie erfolgen falls:
● R1 oder knappen RR <5mm oder
● solitärer Lymphknoten >3cm oder
● mehr als ein tumorbefallener Lymphknoten oder
● ECE+ oder
● T3/T4 oder
● Pn1 (major nerve) oder
● L1 oder
● V1
Adaptiert nach S3-LL: Peters et al., Int J Radiat Oncol Biol Phys., 1993, Lundahl et al., Int J Radiat Oncol Biol Phys., 1998, Ang et al., Int J Radiat Oncol Biol Phys., 2001

Die konkomittierende Chemotherapie zeigte sich in 3 grösseren randomisierten Studien vorteilhaft in Bezug auf das Überleben, im Vergleich zu einer alleinigen adjuvanten Radiotherapie, bei HNSCC mit Hochrisikofaktoren:
● ECE an den befallenen Lymphknoten
● R1 Resektion oder knappen Resektionsränder (<5mm im Gesunden).
Cooper et al, Int J Radiat Oncol Biol Phys, 2012, Bernier et al, N Engl J Med. 2004, Bernier et al., Oncologist, 2005

FÜR ALLGEMEINGÜLTIGE, ADJUVANTE RCT BEI ORL-TUMOREN SIEHE ZUDEM 06_02_10_ORL-adjuvant _2019-10-30.pdf in RAO_Daten


C08:
Radio-onkologische Therapieoptionen bei Speicheldrüsenkarzinomen (Salivary Gland Carcinoma):

Rechtfertigende Indikation für die postoperative Radiotherapie...
...der ehemaligen Primärtumorregion:
Aktuell existieren keine prospektiven, randomisierten Studien, die in der Primärsituation bei resektablem Speicheldrüsenkarzinom eine alleinige Tumorresektion mit einer Tumorresektion gefolgt von einer postoperativen Radiotherapie vergleichen. Jedoch konnte in mehreren retrospektiven Studien ein verbessertes Outcome durch eine adjuvante Radiotherapie nachgewiesen werden, falls Faktoren vorliegen, welche die lokale Kontrolle der Erkrankung negativ beeinflussen. Indizierend für eine adjuvante Radiotherapie ist das Vorliegen mindestens eines der folgenden Faktoren:
- high-/intermediate-grade-Tumor mit pT3/pT4 und/oder pN+
- Histologie: Adenoidzystisches Karzinom (ACC)
- R1 oder knapp R0
- Pn1
ESMO Clinical Practice Guideline (2022), Management of Salivary Gland Malignancy: ASCO Guideline (2021), Cheraghlou et al., Head Neck (2018)

...des (elektiven) Halslymphabflusses:
Zusätzlich besteht die Indikation zur postoperativen Radiotherapie der (elektiven) zervikalen Lymphabflussgebiete bei Vorliegen mindestens eines der folgenden Faktoren:
- pN+
- high/intermediate-grade-Tumor mit pT3/4 ohne adäquate Neck Dissektion
Chen et al., Int J Radiat Oncol Biol Phys (2007), Lau et al., Head Neck (2014)



C61:

Prostata – Primäre kurative Radiotherapie:
Die Primäre Radiotherapie des Prostatakarzinoms ist eine zur Operation gleichwertige
kurative Therapieoption. Somit ist für das Prostatakarzinom die primäre alleinige Radiotherapie eine Standardtherapie.
ProtecT, NEJM 2016

Prostata – Primäre SBRT:
Mehrere randomisierte prospektive Phase-III Studien haben ein sehr gutes onkologisches Outcome der Stereotaktischen Bestrahlung der Prostata gezeigt. In einer radomisierten Studie mit über 800 Patienten konnte dabei nach 5 Jahren ein biochemisches Rezidiv-freies Überleben von 95.8% gezeigt werden. Somit ist die SBRT bei Patienten mit low- oder Favourable intermediate-risk Prostatakarzinom eine kurative Therapieoption (Kishan, Jama 2019; van As, NEJM 2024).
Mehrere randomisierte prospektive Phase-III Studien haben ein sehr gutes onkologisches Outcome (5y 84%) mit wenig Nebenwirkungen nach SBRT der Prostata bei unfavourable intermediate und high-risk Prostatakarzinom gezeigt. Somit ist die SBRT bei Patienten mit unfavourable intermediate und high-risk Prostatakarzinom eine kurative Therapieoption (Widmark, Lancet 2019).

Prostata – Adjuvante Radiotherapie:
Die adjuvante Radiotherapie (PSA postop <0.03ng/ml) erfolgt zusätzlich zur Initialtherapie, min. 3 Monate nach radikaler Prostatektomie, mit dem Ziel, das Risiko eines (biochem.) Rezidivs zu senken, das Risiko auf Metastasen zu reduzieren und das Gesamtüberleben zu verbessern.
EAU Guidelines

Prostata - Salvage Radiotherapie:
Bei biochemischem Rezidiv nach Prostatektomie stellt die Salvage-Radiotherapie der Prostataloge die einzige kurative Therapieoption dar. Dabei ist die möglichst frühe Einleitung der Salvage-Radiotherapie mit niedrigem PSA-Wert (<0.5 ng/ml unabhängig vom PSMA-Staging) für das Gesamtüberleben und krankheitsfreie Überleben von Vorteil. (S3-Leitline, Stish BJ, et al. J Clin Oncol 2016). Somit ist beim biochemischen Rezidiv die Salvage-Radiotherapie gemäss S3-Leitlinie Standard und sollte möglichst frühzeitig bei PSA-Wert unter 0.5ng/ml eingeleitet werden.
EAU Guidelines

Prostata - Oligometastasierung:
Die Radiotherapie von Metastasen bei Patienten mit oligometastasiertem Prostatakarzinom kann die Zeit bis zur Einleitung einer Systemtherapie/ADT deutlich erhöhen.
Ost et al, JCO 2018
Die Radiotherapie des Primärtumors bei primär metastasiertem Prostatakarzinom ist bei Patienten mit niedriger Gesamttumorlast mit einem verbesserten Gesamtüberleben (HR 0.68) und krankheitsfreien Überleben (HR 0.59) assoziiert. Somit sollte primär metastasierten Patienten mit geringer Tumorlast und gutem Allgemeinzustand die Radiotherapie des Primärtumors angeboten werden.
EAU Guidelines, STAMPEDE, Parker et al. Lancet 2018
Die stereotaktische Radiotherapie von Oligometastasen (≤5, ossär und viszeral) bei kontrolliertem Primärtumor verbessert das Gesamtüberleben (HR 0.57).
SABR-COMET (Parker et al.) Lancet 2019


M72.2, M76.6, M61.9, H06.2, M77.1, M72.0, M72.2, N48.6, M77.9, M75.9, M17.9, M19.9, N62, L91.0:

Bei benignen Erkrankungen wie entzündliche Prozesse im Bereich von Sehnen und Gelenken sowie bei Arthrosen ist eine niedrigdosierte Radiotherapie eine effektive Therapieoption. Bei proliferativen Erkrankungen im Frühstadium kann eine Bestrahlung eine effektive Therapieoption darstellen.
Folgende gutartige Erkankungen werden am USZ bestrahlt:
• Fasciitis plantaris/ Achillodynie ) (Evidenzgrad 1b, Empfehlungsgrad A)
• Heterotope Ossifikationen (Patienten mit TEP und Entfernung von HO: Evidenzgrad 1, Empfehlungsgrad A; weitere gelenknahe Fx: Evidenzgrad 2, Empfehlungsgrad B)
• Endokrine Orbitopathie (EO) (Evidenzlevel 2, Empfehlungsgrad B)
• Epicondylopathia humeri, Epicondylus humeri radialis oder des Epicondylus humeri ulnaris (Tennis-Ellenbogen) (Evidenzgrad 2c, Empfehlungsgrad B)
• Hyperproliferative Prozesse: M. Dupuytren (Evidenzgrad 2c, Empfehlungsgrad B), M. Ledderhose (Evidenzgrad 4, Empfehlungsgrad 0), Induratio penis plastica (Peyronie’s disease) (Evidenzgrad 3b, Empfehlungsgrad 0)
• Enthesiopathien z.B.Bursitis trochanterica (Evidenzgrad 4, Empfehlungsgrad 0)
• Periarthropathia humeroscapularis (Schulter-Syndrom) (Evidenzgrad 4, Empfehlungsgrad 0) Gonarthrose
• Gynäkomastie (Evidenzgrad, Empfehlungsgrad A)
• Keloid (Evidenzgrad 4, Empfehlungsgrad 0)
Die Indikationsstellung erfolgt durch den behandelnden Facharzt.
DEGRO Guidelines, S2e-Leitlinie, aktuelle Version 11/2018, https://www.degro.org/wp-content/uploads/2018/11/S2-Leitlinie-Strahlentherapie-
"""
    
    indication_map = {}
    
    # Regex, um Zeilen zu finden, die mit ICD-Codes und einem Doppelpunkt beginnen.
    # Dieses Muster wird verwendet, um die Startpunkte der einzelnen Blöcke zu finden.
    pattern = re.compile(r"^(?P<codes>([A-Z][0-9A-Z]{1,2}(\.\w+)?(?:,\s*)?)+):\s*$", re.MULTILINE)
    
    # Finde alle Übereinstimmungen (Marker) im Text und speichere sie in einer Liste.
    matches = list(pattern.finditer(source_text))
    
    for i, match in enumerate(matches):
        # Der Start des aktuellen Textblocks ist das Ende der Zeile des aktuellen Markers.
        start_of_text = match.end()
        
        # Das Ende des aktuellen Textblocks ist der Anfang des nächsten Markers,
        # oder das Ende des gesamten Strings, wenn es der letzte Marker ist.
        end_of_text = matches[i+1].start() if i + 1 < len(matches) else len(source_text)
        
        # Extrahiere den Textblock und bereinige führende/nachfolgende Leerzeichen/Zeilenumbrüche.
        text_block = source_text[start_of_text:end_of_text].strip()
        
        # Hole die Code-Zeichenkette aus dem aktuellen Marker.
        code_header = match.group('codes')
        codes = [code.strip() for code in code_header.split(',')]
        
        for code in codes:
            if code:
                # Füge jeden Code zum Dictionary hinzu. Der Text ist identisch.
                indication_map[code] = text_block
                
    return indication_map

def get_indication_text(icd_code, indication_map):
    """
    Ruft den Indikationstext für einen gegebenen ICD-10-Code ab.

    Implementiert eine hierarchische Suche:
    1. Sucht nach einer exakten Übereinstimmung (z.B. C34.9).
    2. Wenn keine exakte Übereinstimmung gefunden wird, sucht es nach dem 
       übergeordneten Code (z.B. sucht nach C34, wenn C34.9 angefragt wurde).
    
    Args:
        icd_code (str): Der abzufragende ICD-10-Code.
        indication_map (dict): Das Dictionary mit den Code-Text-Mappings.

    Returns:
        str: Der gefundene Indikationstext.
        None: Wenn weder der exakte Code noch ein übergeordneter Code gefunden wurde.
    """
    # 1. Suche nach exakter Übereinstimmung
    if icd_code in indication_map:
        return indication_map[icd_code]
    
    # 2. Wenn keine exakte Übereinstimmung, suche nach übergeordnetem Code
    if '.' in icd_code:
        parent_code = icd_code.split('.')[0]
        if parent_code in indication_map:
            return indication_map[parent_code]
            
    # 3. Wenn nichts gefunden wurde
    return None

# Dieser Block wird nur ausgeführt, wenn das Skript direkt gestartet wird.
if __name__ == '__main__':
    # Erstelle das Mapping einmal beim Start
    master_indication_map = create_indication_mapping()

    print("--- DEMONSTRATION DER FUNKTIONALITÄT ---\n")

    # Testfall 2: Hierarchische Suche - spezifischer Code NICHT vorhanden, aber Parent vorhanden
    print("Suche nach 'C34.x':")
    text = get_indication_text('C34.9', master_indication_map)
    print(f"{text}\n" if text else "Nicht gefunden.\n")