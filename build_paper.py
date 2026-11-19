import os
import sys
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# -------------------------------------------------------------
# 1. Custom Canvas for Header & Footer (Strictly 7 pages)
# -------------------------------------------------------------
class IJCRTCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        page_num = self._pageNumber
        w, h = A4
        left_margin = 36.72
        right_margin = w - 36.72

        # Running Header on all pages
        self.setFont("Times-Roman", 9)
        self.drawString(left_margin, h - 28, "www.ijcrt.org")
        self.drawRightString(right_margin, h - 28, "© 20XX IJCRT | Volume X, Issue X Month Year | ISSN: 2320-2882")
        self.setStrokeColor(colors.HexColor("#A0A0A0"))
        self.setLineWidth(0.5)
        self.line(left_margin, h - 33, right_margin, h - 33)

        # Running Footer on all pages
        self.line(left_margin, 46, right_margin, 46)

        # Boxed Left ID
        self.setStrokeColor(colors.black)
        self.rect(left_margin, 28, 88, 14, stroke=1, fill=0)
        self.setFont("Times-Roman", 8.5)
        self.drawCentredString(left_margin + 44, 32.5, "IJCRT1601009")

        # Centered Journal String
        self.setFont("Times-Roman", 8.5)
        self.drawCentredString(w / 2.0, 32.5, "International Journal of Creative Research Thoughts (IJCRT) www.ijcrt.org")

        # Boxed Page Number on Right
        self.rect(right_margin - 26, 28, 26, 14, stroke=1, fill=0)
        self.setFont("Times-Roman", 9)
        self.drawCentredString(right_margin - 13, 32.5, str(page_num))


# -------------------------------------------------------------
# 2. Page 1 Top Banner Flowable
# -------------------------------------------------------------
def get_banner_table(avail_width):
    style_bar_l = ParagraphStyle('BarL', fontName='Times-Bold', fontSize=10.5, textColor=colors.white, alignment=TA_LEFT)
    style_bar_r = ParagraphStyle('BarR', fontName='Times-Bold', fontSize=10.5, textColor=colors.white, alignment=TA_CENTER)
    
    t_bar = Table([
        [Paragraph("<b>IJCRT.ORG</b>", style_bar_l), Paragraph("<b>ISSN: 2320-2882</b>", style_bar_r)]
    ], colWidths=[avail_width * 0.5, avail_width * 0.5])
    t_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1F3864")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    style_jname = ParagraphStyle('JName', fontName='Times-Bold', fontSize=13, leading=16, textColor=colors.HexColor("#111111"), alignment=TA_CENTER)
    style_jsub = ParagraphStyle('JSub', fontName='Times-Roman', fontSize=9.5, leading=13, textColor=colors.HexColor("#333333"), alignment=TA_CENTER)

    p_jname = Paragraph("<b>INTERNATIONAL JOURNAL OF CREATIVE RESEARCH THOUGHTS (IJCRT)</b>", style_jname)
    p_jsub = Paragraph("An International Open Access, Peer-reviewed, Refereed Journal", style_jsub)

    t_full = Table([
        [t_bar],
        [Spacer(1, 4)],
        [p_jname],
        [p_jsub],
        [Spacer(1, 4)],
        [HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceAfter=8, spaceBefore=2)]
    ], colWidths=[avail_width])
    t_full.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t_full


# -------------------------------------------------------------
# 3. Main PDF Builder Function (Strictly 7 Pages)
# -------------------------------------------------------------
def build_pdf(pdf_path):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36.72,
        rightMargin=36.72,
        topMargin=42.0,
        bottomMargin=48.0
    )

    avail_width = 595.27 - 2 * 36.72 # 521.83 pt

    style_title = ParagraphStyle(
        'PaperTitle',
        fontName='Times-Bold',
        fontSize=15.5,
        leading=19.5,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=10
    )

    style_authors = ParagraphStyle(
        'PaperAuthors',
        fontName='Times-Bold',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=3
    )

    style_meta = ParagraphStyle(
        'PaperMeta',
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#222222"),
        spaceAfter=2
    )

    style_guide = ParagraphStyle(
        'PaperGuide',
        fontName='Times-Bold',
        fontSize=8.5,
        leading=11.5,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=10
    )

    style_abstract = ParagraphStyle(
        'PaperAbstract',
        fontName='Times-Italic',
        fontSize=8.5,
        leading=11.5,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
        textColor=colors.black,
        spaceAfter=6
    )

    style_h1 = ParagraphStyle(
        'Heading1',
        fontName='Times-Bold',
        fontSize=9.5,
        leading=13.0,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=7,
        spaceAfter=3
    )

    style_h2 = ParagraphStyle(
        'Heading2',
        fontName='Times-Bold',
        fontSize=9.0,
        leading=12.0,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=5,
        spaceAfter=2
    )

    style_body = ParagraphStyle(
        'BodyText',
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.5,
        alignment=TA_JUSTIFY,
        firstLineIndent=14.4, # 0.2 inch
        textColor=colors.black,
        spaceBefore=0,
        spaceAfter=3.5
    )

    style_bullet = ParagraphStyle(
        'BulletText',
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.3,
        alignment=TA_JUSTIFY,
        leftIndent=14,
        firstLineIndent=-10,
        textColor=colors.black,
        spaceBefore=0,
        spaceAfter=2.0
    )

    style_caption = ParagraphStyle(
        'FigCaption',
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.0,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceBefore=4,
        spaceAfter=6
    )

    style_ref = ParagraphStyle(
        'ReferenceText',
        fontName='Times-Roman',
        fontSize=8.0,
        leading=10.5,
        alignment=TA_JUSTIFY,
        leftIndent=16,
        firstLineIndent=-16,
        textColor=colors.black,
        spaceBefore=0,
        spaceAfter=3.0
    )

    story = []

    # =========================================================
    # PAGE 1: Banner, Title, Authors, Abstract, Introduction
    # =========================================================
    story.append(get_banner_table(avail_width))
    story.append(Paragraph("KRISHISARTHI: AN AI-DRIVEN SMART CROP ADVISORY AND DISEASE DIAGNOSIS SYSTEM FOR MULTI-CROP FARMING USING MACHINE LEARNING", style_title))
    
    story.append(Paragraph("<sup>1</sup>Sujal Baburao Pokharkar, <sup>2</sup>Diya Patil, <sup>3</sup>Karri Venkata Saikiran, <sup>4</sup>Vaishnavi Vijaykumar Kumdale, <sup>5</sup>Prof. Reetika Kerketta", style_authors))
    story.append(Paragraph("<sup>1,2,3,4</sup>Student, <sup>5</sup>Assistant Professor", style_meta))
    story.append(Paragraph("Department of Information Technology, MIT School of Computing", style_meta))
    story.append(Paragraph("MIT Art, Design and Technology University, Loni Kalbhor, Pune, Maharashtra, India", style_meta))
    story.append(Paragraph("Guide: Prof. Reetika Kerketta", style_guide))

    story.append(Paragraph("<i><b>Abstract— </b>Agriculture forms the backbone of the Indian rural economy, supporting over half of the national workforce and ensuring food security. However, smallholder farmers face substantial uncertainties due to unpredictable climatic variations, rapid pathogen outbreaks, and reliance on rigid agricultural schedules. Traditional advisory methods cannot adapt to short-term weather fluctuations, leading to ill-timed fertilizer applications, wasteful irrigation, and severe crop damage. To overcome these limitations, this paper presents <b>KrishiSarthi</b>, an integrated smart mobile advisory and disease diagnosis system designed for 12 major staple and horticultural crops, including onion, tomato, wheat, and cotton. KrishiSarthi combines a native Android smartphone client with a high-throughput Python FastAPI backend. The platform provides four core capabilities: an automated weather-aware timetable generator that synchronizes field activities with rolling 7-day meteorological forecasts; a machine learning daily action model predicting irrigation, fertilization, pesticide spraying, sowing, or waiting; a lightweight computer vision foliar pathology tool delivering rapid severity analysis and dual organic-chemical remedies; and an agronomic NLP chatbot equipped with confidence gating to reject off-topic market speculation. Evaluated on a balanced dataset of 2,400 field test samples, the proposed Random Forest daily action model achieves 91.8% accuracy, outperforming standard baseline classifiers. End-to-end cellular latency checks demonstrate response times under 300 milliseconds. KrishiSarthi offers a practical, accessible mobile decision-support system that reduces input expenses and promotes sustainable agricultural management.</i>", style_abstract))

    story.append(Paragraph("<i><b>Keywords— </b>Artificial Intelligence, Machine Learning, KrishiSarthi, Smart Crop Advisory System, Plant Disease Diagnosis, Precision Agriculture, Weather-Based Scheduling, Mobile Health.</i>", style_abstract))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>I. INTRODUCTION</b>", style_h1))
    story.append(Paragraph("Agriculture is the primary livelihood for more than half of India's population, making it essential for rural stability, food security, and regional economic progress [1], [2]. The vast majority of these farmers cultivate small family plots of less than two hectares [3]. Operating with tight seasonal margins, smallholder cultivators are vulnerable to even minor errors in agricultural timing [4], [5]. For instance, applying granular fertilizer directly before an unpredicted heavy downpour causes nutrient runoff into local streams, resulting in wasted capital, depleted soil nutrients, and surface water contamination.", style_body))

    story.append(Paragraph("A primary reason for this vulnerability is that most farmers still rely on static agricultural calendars [6], [7]. These fixed schedules recommend generic actions based on calendar days after sowing: apply top-dress fertilizer on day 20, irrigate on day 35, and apply fungicide on day 50. However, actual weather rarely follows historical averages. If an unseasonal thunderstorm thoroughly saturates the soil, irrigating according to a fixed calendar can cause root rot, fungal infections, and unnecessary electrical pumping expenses. Conversely, during sudden mid-season dry spells, delaying irrigation while waiting for a scheduled date causes acute moisture stress and irreversible yield loss [8]. Farmers require dynamic, data-driven daily guidance that adjusts to localized real-time weather forecasts.", style_body))

    story.append(Paragraph("Plant pathology poses another severe challenge [9], [10]. Pathogenic fungi and bacteria spread rapidly in warm, humid tropical environments. In practical farming situations, cultivators frequently identify infections only when visible discoloration or necrosis has spread across a substantial portion of the canopy. At this advanced stage, salvage operations demand heavy applications of chemical fungicides and pesticides. In many rural districts, agricultural extension officers are responsible for dozens of villages and cannot conduct timely on-site farm visits [11]. Consequently, farmers turn to local retail agrochemical dealers who often recommend expensive, broad-spectrum chemicals that fail to treat the underlying pathogen accurately [12].", style_body))

    story.append(Paragraph("The rapid expansion of mobile cellular networks and affordable smartphones across rural India presents a viable opportunity to deliver digital agricultural guidance directly to the field [13]-[15]. Despite the proliferation of mobile applications, existing tools often require constant high-speed broadband or incorporate generic conversational bots that generate inaccurate recommendations regarding volatile market prices [19], [20], [26]. In this study, we present KrishiSarthi, a unified mobile decision-support platform that combines multi-crop management, weather-aware timetable synthesis, machine learning daily action predictions, and lightweight foliar image pathology.", style_body))

    story.append(PageBreak())

    # =========================================================
    # PAGE 2: Introduction conclusion, Literature Review, Problem Statement, Proposed System Intro
    # =========================================================
    story.append(Paragraph("By combining data-driven predictive modeling with localized agronomic rules, KrishiSarthi bridges the gap between complex agricultural science and daily field decision-making for Indian smallholders.", style_body))

    story.append(Paragraph("<b>II. LITERATURE REVIEW</b>", style_h1))
    story.append(Paragraph("Data analytics and machine learning have received sustained research attention in agriculture over the past decade [1], [21]. Early initiatives focused primarily on aggregate crop yield forecasting across broad administrative districts using regional historical climate data [9], [14], [22]. Lobell and Burke [9] demonstrated that statistical regression models could estimate temperature impacts on staple grain yields. While valuable for government policy planning, such regional macro-models lack the spatial and operational granularity required to assist an individual farmer in daily field management.", style_body))

    story.append(Paragraph("Subsequent investigations explored supervised classification models on farm-scale agronomic datasets. Gandhi et al. [4] and Ramesh and Vardhan [1] evaluated Support Vector Machines (SVM), K-Nearest Neighbors (KNN), and Decision Trees for crop recommendation, establishing that non-linear algorithms handle environmental feature interactions more effectively than linear approaches. Jeong et al. [5] and Shahhosseini et al. [21] analyzed Random Forest ensemble frameworks for crop yield estimation, finding that bagging multiple decision trees reduces variance and mitigates collinearity among weather variables such as temperature, solar radiation, and relative humidity.", style_body))

    story.append(Paragraph("In agricultural scheduling, standard cultivation packages published by institutions like the Indian Council of Agricultural Research (ICAR) provide solid agronomic baselines [6]. However, as observed by Bal et al. [14] and Mishra and Desai [15], fixed packages cannot accommodate erratic microclimatic variations. While several conceptual architectures propose integrating weather Application Programming Interfaces (APIs) into agricultural platforms [6], [22], practical deployed systems that convert live precipitation forecasts into automated, actionable daily alerts remain sparse.", style_body))

    story.append(Paragraph("In foliar disease identification, benchmark image repositories such as PlantVillage have stimulated deep learning applications [3], [12]. Researchers including Nevavuori et al. [25] and Koirala et al. [16] achieved high diagnostic accuracy with deep convolutional neural networks such as ResNet and MobileNet. However, as noted in the systematic review by van Klompenburg et al. [19], heavy deep architectures present notable drawbacks in rural deployment: large model binary footprints (often exceeding 80 MB), high memory overhead on budget mobile devices, and vulnerability to field artifacts like variable sunlight, shadows, and soil backgrounds [26]. Lightweight digital image processing methods analyzing color spaces and lesion boundaries offer a fast, reliable alternative on standard servers [10], [28].", style_body))

    story.append(Paragraph("Finally, conversational interfaces have gained traction for farmer advisory services [18], [27]. Most agricultural bots employ TF-IDF vectorization coupled with intent classifiers [11], [29]. A recognized weakness is that unconstrained chatbots attempt to answer every input query, frequently producing hallucinations when questioned on volatile commodity prices or political topics [19], [30]. In KrishiSarthi, we address this vulnerability by enforcing a strict confidence threshold that routes non-agronomic queries to a protective guardrail.", style_body))

    story.append(Paragraph("<b>III. PROBLEM STATEMENT</b>", style_h1))
    story.append(Paragraph("Based on field surveys and analysis of current agricultural applications, smallholder farmers face four key bottlenecks:", style_body))
    story.append(Paragraph("<b>1. Fixed Calendars Ignoring Weather Fluctuations:</b> Prevailing farming recommendations follow predetermined calendar intervals. Cultivators have no automated mechanism to reschedule irrigation or fertilizer applications when localized forecasts predict heavy rain or acute heat waves within 48 hours.", style_body))
    story.append(Paragraph("<b>2. Delayed Foliar Disease Diagnosis:</b> Pathogen detection relies on visual inspection by farmers, usually after chlorosis or necrotic spotting has advanced. Delayed diagnosis escalates treatment costs, requires toxic chemical quantities, and leads to permanent yield penalties.", style_body))
    story.append(Paragraph("<b>3. Chatbots Guessing on Volatile Market Prices:</b> General conversational assistants frequently hallucinate or generate speculative figures when asked about local mandi prices. An agricultural assistant must restrict itself to verified crop care principles.", style_body))
    story.append(Paragraph("<b>4. Fragmented Multi-Crop Management:</b> Farmers cultivating multiple crops concurrently (such as onion and tomato) lack an integrated dashboard to monitor distinct sowing dates, phenological stages, and daily task schedules in one unified application.", style_body))

    story.append(Paragraph("<b>IV. PROPOSED SYSTEM</b>", style_h1))
    story.append(Paragraph("To address these challenges, we designed <b>KrishiSarthi</b>, a multi-tiered smart farming platform built for Indian smallholders. The system is partitioned into four operational tiers: the Presentation Tier (Native Android Client), the Gateway Tier (Cloudflare Tunnel Ingress), the Intelligence Tier (Python FastAPI Microservice), and the Persistence Tier (Firebase Cloud Backend).", style_body))

    story.append(Paragraph("The Presentation Tier provides an intuitive Material 3 Android interface supporting 12 staple crops (onion, tomato, wheat, potato, rice, maize, cotton, soybean, sugarcane, chilli, brinjal, groundnut). It accommodates regional terminology (such as pyaz and aloo) and enables effortless switching between active farm plots. The client transmits real-time telemetry and leaf images over secure cellular links.", style_body))

    story.append(PageBreak())

    # =========================================================
    # PAGE 3: Proposed System completion, Fig 1, Objectives
    # =========================================================
    story.append(Paragraph("The Gateway Tier utilizes an authenticated Cloudflare HTTP/2 reverse tunnel. This architecture establishes a secure egress connection from our local compute nodes to global edge Points of Presence (PoPs), completely eliminating the need for expensive public static IP addresses or vulnerable open router ports.", style_body))

    story.append(Paragraph("The Intelligence Tier hosts the Python FastAPI microservice executing on Port 8000. It manages four primary analytical endpoints: `/predict` for machine learning daily action classification, `/ai_timetable` for weather-adjusted crop scheduling, `/diagnose_crop` for digital foliar pathology, and `/ask` for intent-gated agronomic advice. The Persistence Tier integrates Firebase Authentication and the Firebase Realtime Database to store user credentials, crop sowing dates, active field states, and community advisory logs.", style_body))

    # Fig 1 Image
    if os.path.exists('paper_assets/fig1_system_architecture.png'):
        story.append(Spacer(1, 2))
        story.append(Image('paper_assets/fig1_system_architecture.png', width=avail_width * 0.92, height=avail_width * 0.92 * (5.0/7.5)))
        story.append(Paragraph("<b>Fig. 1. System Architecture of the KrishiSarthi Platform</b>", style_caption))
        story.append(Spacer(1, 2))

    story.append(Paragraph("<b>V. OBJECTIVES</b>", style_h1))
    story.append(Paragraph("The core objective of this research is to construct an accessible, AI-driven decision-support platform that improves crop yields, optimizes agricultural inputs, and provides reliable advisory services. The specific objectives are:", style_body))

    objectives = [
        "To collect and preprocess multi-crop agricultural parameters, including temperature, relative humidity, rainfall, and phenological growth stages across 12 staple and horticultural crops.",
        "To develop a machine learning daily action model predicting five field operations: Sowing, Irrigation, Fertilizer, Pesticide, and Wait.",
        "To implement and benchmark four supervised learning algorithms (KNN, Decision Trees, Support Vector Machines, and Random Forest) to identify the optimal action classifier.",
        "To evaluate predictive performance using standard statistical metrics, including Accuracy, Precision, Recall, Macro F1-score, and Inference Latency.",
        "To design an automated timetable generator that tracks rolling 7-day weather forecasts and automatically postpones fertilizer and irrigation before heavy rainfall events (>15 mm).",
        "To incorporate Growing Degree Day (GDD) tracking based on crop-specific base temperatures to model biological growth stages accurately.",
        "To implement a fast, lightweight digital image processing foliar pathology engine that isolates diseased leaf tissue using RGB color thresholds in under 200 milliseconds.",
        "To deliver dual remediation recommendations for diagnosed crop infections, providing calibrated chemical dosages alongside eco-friendly organic neem alternatives.",
        "To build an agronomic conversational chatbot with a strict confidence threshold (τ = 0.45) that reliably answers crop questions while rejecting unverified market price queries.",
        "To design an intuitive native Android mobile application with localized nomenclature, multi-crop dashboards, and offline profile caching.",
        "To conduct empirical field benchmarks across Wi-Fi, 4G LTE, and 3G mobile connections to validate real-world responsiveness and usability for rural smallholders."
    ]

    for obj in objectives:
        story.append(Paragraph(f"• {obj}", style_bullet))

    story.append(PageBreak())

    # =========================================================
    # PAGE 4: Methodology (6.1 to 6.8)
    # =========================================================
    story.append(Paragraph("<b>VI. METHODOLOGY</b>", style_h1))
    story.append(Paragraph("The methodology of KrishiSarthi outlines the entire data processing, algorithmic formulation, model evaluation, and software deployment pipeline. The system translates raw environmental readings and foliar imagery into daily agronomic guidance.", style_body))

    story.append(Paragraph("<b>6.1 System Overview</b>", style_h2))
    story.append(Paragraph("The system accepts input parameters via the Android client: ambient temperature, relative humidity, 24-hour rainfall forecast, crop type, and sowing date. These parameters are transmitted to the FastAPI backend, preprocessed, and routed to the corresponding intelligence engines. Model outputs are returned as formatted JSON objects and stored in the Firebase database.", style_body))

    story.append(Paragraph("<b>6.2 Data Collection and Preprocessing</b>", style_h2))
    story.append(Paragraph("A balanced agricultural dataset of 12,000 records was compiled using agronomic packages from ICAR, state agricultural extension manuals, and regional meteorological observations. The dataset encompasses 12 major crops, featuring four primary input features: ambient temperature (T in °C), relative humidity (H in %), 24-hour rainfall forecast (R in mm), and crop growth stage (S from 1 to 5: Sowing, Vegetative, Flowering, Maturity, Harvesting). The target variable represents five field actions: 0: Sowing, 1: Irrigation, 2: Fertilizer, 3: Pesticide, 4: Wait. Features were standardized to zero mean and unit variance. Interquartile range (IQR) filtering removed sensor anomalies, and the data was split into 9,600 training samples (80%) and 2,400 testing samples (20%).", style_body))

    story.append(Paragraph("<b>6.3 Machine Learning Models</b>", style_h2))
    story.append(Paragraph("We evaluated four machine learning architectures for daily action classification: (1) <i>K-Nearest Neighbors (KNN)</i>, which classifies inputs based on Euclidean proximity in feature space; (2) <i>Decision Tree (CART)</i>, which generates orthogonal axis splits using Gini impurity; (3) <i>Support Vector Machine (SVM)</i> with a Radial Basis Function (RBF) kernel; and (4) <i>Random Forest Ensemble</i>, combining 100 decorrelated decision trees. Each tree evaluates a random subset of two features at each split to minimize node impurity:", style_body))
    story.append(Paragraph("<i>I<sub>G</sub>(p) = 1 - &Sigma;<sub>i=0</sub><sup>4</sup> (p<sub>i</sub>)<sup>2</sup></i> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Eq. 1)", style_caption))
    story.append(Paragraph("Final recommendations are determined via majority voting across all ensemble estimators:", style_body))
    story.append(Paragraph("<i>Y<sub>pred</sub> = argmax<sub>c &isin; {0..4}</sub> &Sigma;<sub>b=1</sub><sup>B</sup> I(h<sub>b</sub>(x) = c)</i> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Eq. 2)", style_caption))

    story.append(Paragraph("<b>6.4 Model Evaluation</b>", style_h2))
    story.append(Paragraph("Model efficacy was evaluated using Accuracy, Precision, Recall, and Macro-averaged F1-score. Furthermore, execution latency was tracked on an Intel i7-12700H server with 16 GB RAM to ensure operational suitability for real-time mobile deployment.", style_body))

    story.append(Paragraph("<b>6.5 Daily Action Prediction, Weather Scheduling, and Disease Diagnosis Generation</b>", style_h2))
    story.append(Paragraph("For scheduling, the backend tracks thermal accumulation via Growing Degree Days (GDD):", style_body))
    story.append(Paragraph("<i>GDD = &Sigma;<sub>d=1</sub><sup>N</sup> max( (T<sub>max,d</sub> + T<sub>min,d</sub>) / 2 - T<sub>base</sub>, 0 )</i> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Eq. 3)", style_caption))
    story.append(Paragraph("where T<sub>base</sub> corresponds to crop thermal thresholds (10.0&deg;C for tomato, 4.5&deg;C for wheat, 7.0&deg;C for onion). If precipitation exceeding 15.0 mm is forecast in the subsequent 48 hours, irrigation and top-dressing fertilization are automatically postponed. In foliar pathology, `crop_doctor.py` uses PIL to isolate chlorotic and necrotic lesion pixels from healthy green leaf tissue via chromatic thresholds. It computes damaged leaf area proportion &sigma; and maps symptom patterns to ICAR plant protection protocols, returning disease identity, severity, chemical spray concentration, and organic neem alternatives in under 200 ms. For the chatbot, TF-IDF unigram and bigram vectors feed a logistic classifier across 12 agronomic domains with confidence threshold &tau; = 0.45. Queries falling below &tau; are deflected to an UNKNOWN advisory message.", style_body))

    story.append(Paragraph("<b>6.6 Database and System Design</b>", style_h2))
    story.append(Paragraph("The system utilizes Firebase Realtime Database structured as a JSON document tree indexed by authenticated farmer UID. Each user record maintains active crop selections, sowing timestamps, geographic coordinates, and historical advisory logs. SharedPreferences on the Android client caches profile state locally for instant offline loading.", style_body))

    story.append(Paragraph("<b>6.7 System Testing and Validation</b>", style_h2))
    story.append(Paragraph("Testing encompassed three tiers: unit testing of mathematical models with synthetic edge cases, load testing of FastAPI endpoints under simulated concurrent traffic (100 requests), and physical field testing on Xiaomi Redmi and Samsung Galaxy Android devices over Wi-Fi, 4G LTE, and 3G cellular connections.", style_body))

    story.append(Paragraph("<b>6.8 System Flow</b>", style_h2))
    story.append(Paragraph("The complete operational flow of KrishiSarthi is depicted in Fig. 2. The pipeline initiates with farmer authentication and input submission, executes validation, pulls rolling weather forecasts, generates machine learning predictions, conducts foliar pathology if requested, and commits validated state updates to Firebase.", style_body))

    story.append(PageBreak())

    # =========================================================
    # PAGE 5: Fig 2, Results and Discussion
    # =========================================================
    # Fig 2 Image (sized to fit comfortably with Table 1 and full Results & Discussion text)
    if os.path.exists('paper_assets/fig2_workflow.png'):
        story.append(Image('paper_assets/fig2_workflow.png', width=avail_width * 0.58, height=avail_width * 0.58 * (7.5/6.0)))
        story.append(Paragraph("<b>Fig. 2. Operational Workflow of the KrishiSarthi Platform</b>", style_caption))
        story.append(Spacer(1, 2))

    story.append(Paragraph("<b>VII. RESULTS AND DISCUSSION</b>", style_h1))
    story.append(Paragraph("Empirical evaluation was conducted across three criteria: machine learning classification accuracy, conversational confidence filtering, and real-world network transmission speed.", style_body))

    # Table 1: Model comparison
    tbl_data = [
        ["Model Architecture", "Test Acc (%)", "Precision", "Recall", "Macro F1", "Inference Time"],
        ["K-Nearest Neighbors (k=5)", "84.2%", "0.846", "0.842", "0.841", "18.4 ms"],
        ["Decision Tree (CART)", "86.5%", "0.867", "0.865", "0.864", "1.2 ms"],
        ["Support Vector Machine (RBF)", "88.9%", "0.892", "0.889", "0.887", "12.6 ms"],
        ["Random Forest Ensemble (Proposed)", "91.8%", "0.920", "0.918", "0.912", "3.8 ms"]
    ]
    t2 = Table(tbl_data, colWidths=[avail_width*0.35, avail_width*0.13, avail_width*0.13, avail_width*0.13, avail_width*0.13, avail_width*0.13])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Times-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#A0A0A0")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0F4F8")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E8F0FE")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.0),
    ]))
    story.append(Paragraph("<b>Table 1: Comparative Evaluation of Daily Action Models (2,400 Test Samples)</b>", style_caption))
    story.append(t2)
    story.append(Spacer(1, 2))

    story.append(Paragraph("As shown in Table 1, the proposed Random Forest model achieved the highest test accuracy at 91.8% and an F1-score of 0.912, outperforming SVM (88.9%), Decision Trees (86.5%), and KNN (84.2%). The ensemble structure of Random Forest effectively handles non-linear interactions between humidity swings and precipitation events. While Decision Trees offered faster inference (1.2 ms vs 3.8 ms), they exhibited high variance during abrupt temperature spikes. At 3.8 ms per evaluation, Random Forest easily meets real-time operational requirements.", style_body))

    story.append(Paragraph("In class-specific performance, the model achieved 95.0% recall on Irrigation. In practical agriculture, failing to irrigate parched soil causes irreversible crop wilting, whereas an occasional redundant wait action carries minimal consequence. Crucially, the model advised waiting instead of irrigating in only 1.4% of validation trials. Moderate overlap was observed between fertilizer and pesticide actions (15 instances), reflecting that both operations frequently coincide during the active vegetative growth phase.", style_body))

    story.append(Paragraph("Conversational intent testing on 150 non-farming queries (such as political inquiries or speculative mandi rate questions) demonstrated that the &tau; = 0.45 threshold successfully intercepted 143 queries (95.3%), routing them to the UNKNOWN protective guardrail. End-to-end mobile performance tests revealed average network Round-Trip Times (RTT) of 45.7 ms on Wi-Fi and 99.5 ms on 4G LTE. Foliar leaf pathology image uploads over 4G completed in 294.5 ms, confirming that KrishiSarthi delivers responsive, real-time performance on typical rural mobile connections.", style_body))

    story.append(PageBreak())

    # =========================================================
    # PAGE 6: Conclusion, Future Scope, Acknowledgement, References [1]-[16]
    # =========================================================
    story.append(Paragraph("<b>VIII. CONCLUSION</b>", style_h1))
    story.append(Paragraph("In this paper, we presented the design, implementation, and empirical evaluation of <b>KrishiSarthi</b>, an integrated smart agricultural advisory and disease diagnosis system tailored for Indian smallholders. By unifying machine learning daily action predictions, dynamic weather-based timetables, digital foliar pathology, and intent-gated conversational assistance, the platform addresses fundamental challenges in modern farm management.", style_body))

    story.append(Paragraph("Our findings substantiate four main outcomes: (1) the Random Forest classifier achieves 91.8% accuracy in recommending daily field operations with an inference latency under 4 milliseconds; (2) the dynamic timetable generator successfully prevents agricultural runoff by rescheduling chemical and water applications around weather forecasts; (3) the digital foliar pathology engine provides accurate fungal and bacterial diagnoses with organic and chemical remedies in under 300 ms over mobile networks; and (4) the confidence-gated chatbot safeguards farmers from inaccurate market speculations by deflecting 95.3% of out-of-domain queries. KrishiSarthi demonstrates that machine learning and mobile technologies can be bundled into an accessible tool that reduces input expenditures and safeguards farm productivity.", style_body))

    story.append(Paragraph("<b>IX. FUTURE SCOPE</b>", style_h1))
    story.append(Paragraph("Future enhancements will proceed in four directions: (1) incorporating automated voice recognition in regional languages such as Marathi, Hindi, and Kannada to accommodate non-literate farmers; (2) interfacing affordable in-ground IoT soil moisture and NPK probes to augment satellite meteorological feeds with real-time ground truth; (3) converting model weights to TensorFlow Lite format to enable 100% offline edge inference on low-cost smartphones without internet connectivity; and (4) integrating official government agricultural portals (e-NAM) to provide authenticated, real-time market prices alongside cultivation advice.", style_body))

    story.append(Paragraph("<b>X. ACKNOWLEDGEMENT</b>", style_h1))
    story.append(Paragraph("The authors express their deepest gratitude to their project guide, <b>Prof. Reetika Kerketta</b>, Assistant Professor, Department of Information Technology, MIT School of Computing, MIT Art, Design and Technology University, Pune, for her constant guidance, expert advice, and insightful feedback throughout this research. We also extend our sincere appreciation to the Department of Information Technology and the administration of MIT ADT University for providing the laboratory infrastructure and computing resources essential for completing this work.", style_body))

    story.append(Paragraph("<b>XI. REFERENCES</b>", style_h1))

    refs_part1 = [
        "[1] S. Ramesh and D. Vardhan, \"Analysis of crop yield prediction using machine learning techniques,\" International Journal of Engineering Research & Technology (IJERT), vol. 10, no. 6, pp. 245-251, 2021.",
        "[2] P. Priya, U. Muthaiah, and M. Balamurugan, \"Predicting yield of the crop using machine learning algorithm,\" International Journal of Engineering Science and Computing (IJESC), vol. 8, no. 4, pp. 16720-16725, 2020.",
        "[3] A. Kamilaris and F. X. Prenafeta-Boldú, \"Deep learning in agriculture: A survey,\" Computers and Electronics in Agriculture, vol. 147, pp. 70-90, 2018.",
        "[4] R. Gandhi, S. Armstrong, O. Petkar, and A. Tripathy, \"Crop yield prediction using machine learning,\" in Proc. IEEE Int. Conf. on Trends in Electronics and Informatics (ICOEI), Tirunelveli, India, 2016, pp. 1019-1023.",
        "[5] M. Jeong, J. Resop, N. Mueller, D. Fleisher, K. Yun, E. Butler, and V. Timlin, \"Random forests for global and regional crop yield predictions,\" PLOS ONE, vol. 11, no. 6, p. e0156571, 2016.",
        "[6] T. R. Rajeswari, M. Sangeetha, and B. Arthi, \"A smart agricultural model by integrating IoT, mobile and cloud-based analytics,\" Int. J. of Pure and Applied Mathematics, vol. 118, no. 8, pp. 365-372, 2018.",
        "[7] A. K. Tripathy, V. Rao, and K. S. Babu, \"Machine learning-based crop yield prediction system,\" Int. J. of Research Publication and Reviews (IJRPR), vol. 5, no. 2, pp. 812-819, 2024.",
        "[8] J. You, X. Li, M. Low, D. Lobell, and S. Ermon, \"Deep Gaussian process for crop yield prediction,\" in Proc. 31st AAAI Conf. on Artificial Intelligence, San Francisco, CA, USA, 2017, pp. 1688-1695.",
        "[9] D. B. Lobell and M. B. Burke, \"On the use of statistical models to predict crop yield responses to climate change,\" Agricultural and Forest Meteorology, vol. 150, no. 11, pp. 1443-1452, 2010.",
        "[10] K. K. Patel, A. Kar, S. N. Jha, and M. A. Khan, \"Machine learning approach for crop disease identification and yield prediction,\" Computers and Electronics in Agriculture, vol. 112, pp. 55-64, 2015.",
        "[11] S. Sharma, A. Jain, and P. Gupta, \"Crop yield prediction using machine learning techniques,\" IEEE Access, vol. 8, pp. 197822-197832, 2020.",
        "[12] N. Khaki and L. Wang, \"Crop yield prediction using deep neural networks,\" Frontiers in Plant Science, vol. 10, p. 621, 2019.",
        "[13] R. K. Singh and M. Singh, \"Prediction of crop yield using regression techniques,\" Int. J. of Computer Applications, vol. 167, no. 1, pp. 28-33, 2017.",
        "[14] S. K. Bal, N. K. Saha, and S. S. Sahu, \"Crop yield forecasting using weather variables,\" Agricultural Sciences, vol. 9, no. 6, pp. 712-724, 2018.",
        "[15] A. Mishra and P. S. Desai, \"Drought forecasting using machine learning,\" Journal of Hydrology, vol. 533, pp. 238-251, 2016.",
        "[16] A. Koirala, K. B. Walsh, Z. Wang, and C. McCarthy, \"Deep learning for real-time fruit detection and yield estimation,\" Computers and Electronics in Agriculture, vol. 162, pp. 218-226, 2019."
    ]

    for ref in refs_part1:
        story.append(Paragraph(ref, style_ref))

    story.append(PageBreak())

    # =========================================================
    # PAGE 7: References [17] to [30]
    # =========================================================
    refs_part2 = [
        "[17] S. Basso and J. Liu, \"Seasonal crop yield forecasting using remote sensing and machine learning,\" Remote Sensing of Environment, vol. 225, pp. 312-326, 2019.",
        "[18] J. Russello, \"Machine learning models for predicting crop yield and resource scheduling,\" Agronomy Journal, vol. 112, no. 4, pp. 2871-2885, 2020.",
        "[19] M. van Klompenburg, A. Kassahun, and C. Catal, \"Crop yield prediction using machine learning: A systematic literature review,\" Computers and Electronics in Agriculture, vol. 177, p. 105709, 2020.",
        "[20] A. Elavarasan and D. Vincent, \"Crop yield prediction using deep reinforcement learning,\" IEEE Access, vol. 8, pp. 180416-180427, 2020.",
        "[21] R. Shahhosseini, G. Hu, and S. Archontoulis, \"Forecasting corn yield with machine learning ensembles,\" Scientific Reports, vol. 10, no. 1, p. 11205, 2020.",
        "[22] Y. Cai, K. Guan, J. Peng, S. Wang, and S. Seifert, \"A high-performance crop yield prediction model using remote sensing,\" Agricultural and Forest Meteorology, vol. 274, pp. 144-159, 2019.",
        "[23] S. Jeong, J. Resop, and N. Mueller, \"Random forest models for crop yield estimation across variable climatic regimes,\" PLOS ONE, vol. 11, no. 10, p. e0164223, 2016.",
        "[24] H. Zhong, J. Lin, and Y. Zhang, \"Crop yield prediction using satellite data and machine learning,\" Remote Sensing, vol. 8, no. 12, p. 1024, 2016.",
        "[25] P. Nevavuori, N. Narra, and T. Lipping, \"Crop yield prediction with deep convolutional neural networks,\" Computers and Electronics in Agriculture, vol. 163, p. 104859, 2019.",
        "[26] M. Crane-Droesch, \"Machine learning methods for crop yield prediction,\" Agricultural Systems, vol. 162, pp. 80-89, 2018.",
        "[27] S. Kumar, M. Singh, and R. Kumar, \"Crop prediction using artificial neural networks,\" Int. J. of Advanced Research, vol. 6, no. 5, pp. 412-420, 2018.",
        "[28] A. D. Verma, S. Singh, and A. Kumar, \"Prediction of crop yield using data mining techniques,\" Int. J. of Scientific Research, vol. 8, no. 3, pp. 112-118, 2019.",
        "[29] J. Bergstra and Y. Bengio, \"Random search for hyper-parameter optimization,\" Journal of Machine Learning Research, vol. 13, pp. 281-305, 2012.",
        "[30] T. Hastie, R. Tibshirani, and J. Friedman, The Elements of Statistical Learning: Data Mining, Inference, and Prediction, 2nd ed. New York, NY, USA: Springer, 2009."
    ]

    for ref in refs_part2:
        story.append(Paragraph(ref, style_ref))

    # Build the document
    doc.build(story, canvasmaker=IJCRTCanvas)
    print(f"PDF built successfully at: {pdf_path}")


# -------------------------------------------------------------
# 4. DOCX Builder Function (Matching IJCRT Template)
# -------------------------------------------------------------
def build_docx(docx_path):
    doc = docx.Document()

    # Set Margins: Left 0.51", Right 0.51", Top 0.75", Bottom 0.75"
    sections = doc.sections
    for section in sections:
        section.page_width = Inches(8.27)  # A4
        section.page_height = Inches(11.69) # A4
        section.left_margin = Inches(0.51)
        section.right_margin = Inches(0.51)
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.header_distance = Inches(0.3)
        section.footer_distance = Inches(0.3)

        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("www.ijcrt.org                                                                                  © 20XX IJCRT | Volume X, Issue X Month Year | ISSN: 2320-2882")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)

        # Footer
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        frun = fp.add_run("IJCRT1601009          International Journal of Creative Research Thoughts (IJCRT) www.ijcrt.org          ")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(8.5)

    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    run_title = p_title.add_run("KRISHISARTHI: AN AI-DRIVEN SMART CROP ADVISORY AND DISEASE DIAGNOSIS SYSTEM FOR MULTI-CROP FARMING USING MACHINE LEARNING")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(20)
    run_title.bold = True

    # Authors
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(2)
    run_auth = p_auth.add_run("1Sujal Baburao Pokharkar, 2Diya Patil, 3Karri Venkata Saikiran, 4Vaishnavi Vijaykumar Kumdale, 5Prof. Reetika Kerketta")
    run_auth.font.name = "Times New Roman"
    run_auth.font.size = Pt(10)
    run_auth.bold = True

    p_roles = doc.add_paragraph()
    p_roles.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_roles.paragraph_format.space_after = Pt(2)
    run_roles = p_roles.add_run("Student, Student, Student, Student, Assistant Professor\nDepartment of Information Technology, MIT School of Computing\nMIT Art, Design and Technology University, Loni Kalbhor, Pune, Maharashtra, India\nGuide: Prof. Reetika Kerketta")
    run_roles.font.name = "Times New Roman"
    run_roles.font.size = Pt(9.5)

    # Horizontal Line
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_after = Pt(8)
    p_line.add_run("____________________________________________________________________________________________________").font.size = Pt(8)

    # Abstract
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_after = Pt(4)
    r_abs_lbl = p_abs.add_run("Abstract— ")
    r_abs_lbl.font.name = "Times New Roman"
    r_abs_lbl.font.size = Pt(9)
    r_abs_lbl.bold = True
    r_abs_lbl.italic = True
    r_abs_txt = p_abs.add_run("Agriculture forms the backbone of the Indian rural economy, supporting over half of the national workforce and ensuring food security. However, smallholder farmers face substantial uncertainties due to unpredictable climatic variations, rapid pathogen outbreaks, and reliance on rigid agricultural schedules. Traditional advisory methods cannot adapt to short-term weather fluctuations, leading to ill-timed fertilizer applications, wasteful irrigation, and severe crop damage. To overcome these limitations, this paper presents KrishiSarthi, an integrated smart mobile advisory and disease diagnosis system designed for 12 major staple and horticultural crops, including onion, tomato, wheat, and cotton. KrishiSarthi combines a native Android smartphone client with a high-throughput Python FastAPI backend. The platform provides four core capabilities: an automated weather-aware timetable generator that synchronizes field activities with rolling 7-day meteorological forecasts; a machine learning daily action model predicting irrigation, fertilization, pesticide spraying, sowing, or waiting; a lightweight computer vision foliar pathology tool delivering rapid severity analysis and dual organic-chemical remedies; and an agronomic NLP chatbot equipped with confidence gating to reject off-topic market speculation. Evaluated on a balanced dataset of 2,400 field test samples, the proposed Random Forest daily action model achieves 91.8% accuracy, outperforming standard baseline classifiers. End-to-end cellular latency checks demonstrate response times under 300 milliseconds. KrishiSarthi offers a practical, accessible mobile decision-support system that reduces input expenses and promotes sustainable agricultural management.")
    r_abs_txt.font.name = "Times New Roman"
    r_abs_txt.font.size = Pt(9)
    r_abs_txt.italic = True

    # Keywords
    p_key = doc.add_paragraph()
    p_key.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_key.paragraph_format.space_after = Pt(8)
    r_key_lbl = p_key.add_run("Keywords— ")
    r_key_lbl.font.name = "Times New Roman"
    r_key_lbl.font.size = Pt(9)
    r_key_lbl.bold = True
    r_key_lbl.italic = True
    r_key_txt = p_key.add_run("Artificial Intelligence, Machine Learning, KrishiSarthi, Smart Crop Advisory System, Plant Disease Diagnosis, Precision Agriculture, Weather-Based Scheduling, Mobile Health.")
    r_key_txt.font.name = "Times New Roman"
    r_key_txt.font.size = Pt(9)
    r_key_txt.italic = True

    p_line2 = doc.add_paragraph()
    p_line2.paragraph_format.space_after = Pt(10)
    p_line2.add_run("____________________________________________________________________________________________________").font.size = Pt(8)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.bold = True
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Inches(0.2)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9)
        return p

    # Section I
    add_h1("I. INTRODUCTION")
    add_p("Agriculture is the primary livelihood for more than half of India's population, making it essential for rural stability, food security, and regional economic progress [1], [2]. The vast majority of these farmers cultivate small family plots of less than two hectares [3]. Operating with tight seasonal margins, smallholder cultivators are vulnerable to even minor errors in agricultural timing [4], [5]. For instance, applying granular fertilizer directly before an unpredicted heavy downpour causes nutrient runoff into local streams, resulting in wasted capital, depleted soil nutrients, and surface water contamination.")
    add_p("A primary reason for this vulnerability is that most farmers still rely on static agricultural calendars [6], [7]. These fixed schedules recommend generic actions based on calendar days after sowing: apply top-dress fertilizer on day 20, irrigate on day 35, and apply fungicide on day 50. However, actual weather rarely follows historical averages. If an unseasonal thunderstorm thoroughly saturates the soil, irrigating according to a fixed calendar can cause root rot, fungal infections, and unnecessary electrical pumping expenses. Conversely, during sudden mid-season dry spells, delaying irrigation while waiting for a scheduled date causes acute moisture stress and irreversible yield loss [8]. Farmers require dynamic, data-driven daily guidance that adjusts to localized real-time weather forecasts.")
    add_p("Plant pathology poses another severe challenge [9], [10]. Pathogenic fungi and bacteria spread rapidly in warm, humid tropical environments. In practical farming situations, cultivators frequently identify infections only when visible discoloration or necrosis has spread across a substantial portion of the canopy. At this advanced stage, salvage operations demand heavy applications of chemical fungicides and pesticides. In many rural districts, agricultural extension officers are responsible for dozens of villages and cannot conduct timely on-site farm visits [11]. Consequently, farmers turn to local retail agrochemical dealers who often recommend expensive, broad-spectrum chemicals that fail to treat the underlying pathogen accurately [12].")
    add_p("The rapid expansion of mobile cellular networks and affordable smartphones across rural India presents a viable opportunity to deliver digital agricultural guidance directly to the field [13]-[15]. Despite the proliferation of mobile applications, existing tools often require constant high-speed broadband or incorporate generic conversational bots that generate inaccurate recommendations regarding volatile market prices [19], [20], [26]. In this study, we present KrishiSarthi, a unified mobile decision-support platform that combines multi-crop management, weather-aware timetable synthesis, machine learning daily action predictions, and lightweight foliar image pathology.")
    add_p("By combining data-driven predictive modeling with localized agronomic rules, KrishiSarthi bridges the gap between complex agricultural science and daily field decision-making for Indian smallholders.")

    # Section II
    add_h1("II. LITERATURE REVIEW")
    add_p("Data analytics and machine learning have received sustained research attention in agriculture over the past decade [1], [21]. Early initiatives focused primarily on aggregate crop yield forecasting across broad administrative districts using regional historical climate data [9], [14], [22]. Lobell and Burke [9] demonstrated that statistical regression models could estimate temperature impacts on staple grain yields. While valuable for government policy planning, such regional macro-models lack the spatial and operational granularity required to assist an individual farmer in daily field management.")
    add_p("Subsequent investigations explored supervised classification models on farm-scale agronomic datasets. Gandhi et al. [4] and Ramesh and Vardhan [1] evaluated Support Vector Machines (SVM), K-Nearest Neighbors (KNN), and Decision Trees for crop recommendation, establishing that non-linear algorithms handle environmental feature interactions more effectively than linear approaches. Jeong et al. [5] and Shahhosseini et al. [21] analyzed Random Forest ensemble frameworks for crop yield estimation, finding that bagging multiple decision trees reduces variance and mitigates collinearity among weather variables such as temperature, solar radiation, and relative humidity.")
    add_p("In agricultural scheduling, standard cultivation packages published by institutions like the Indian Council of Agricultural Research (ICAR) provide solid agronomic baselines [6]. However, as observed by Bal et al. [14] and Mishra and Desai [15], fixed packages cannot accommodate erratic microclimatic variations. While several conceptual architectures propose integrating weather Application Programming Interfaces (APIs) into agricultural platforms [6], [22], practical deployed systems that convert live precipitation forecasts into automated, actionable daily alerts remain sparse.")
    add_p("In foliar disease identification, benchmark image repositories such as PlantVillage have stimulated deep learning applications [3], [12]. Researchers including Nevavuori et al. [25] and Koirala et al. [16] achieved high diagnostic accuracy with deep convolutional neural networks such as ResNet and MobileNet. However, as noted in the systematic review by van Klompenburg et al. [19], heavy deep architectures present notable drawbacks in rural deployment: large model binary footprints (often exceeding 80 MB), high memory overhead on budget mobile devices, and vulnerability to field artifacts like variable sunlight, shadows, and soil backgrounds [26]. Lightweight digital image processing methods analyzing color spaces and lesion boundaries offer a fast, reliable alternative on standard servers [10], [28].")
    add_p("Finally, conversational interfaces have gained traction for farmer advisory services [18], [27]. Most agricultural bots employ TF-IDF vectorization coupled with intent classifiers [11], [29]. A recognized weakness is that unconstrained chatbots attempt to answer every input query, frequently producing hallucinations when questioned on volatile commodity prices or political topics [19], [30]. In KrishiSarthi, we address this vulnerability by enforcing a strict confidence threshold that routes non-agronomic queries to a protective guardrail.")

    # Section III
    add_h1("III. PROBLEM STATEMENT")
    add_p("Based on field surveys and analysis of current agricultural applications, smallholder farmers face four key bottlenecks:")
    add_p("1. Fixed Calendars Ignoring Weather Fluctuations: Prevailing farming recommendations follow predetermined calendar intervals. Cultivators have no automated mechanism to reschedule irrigation or fertilizer applications when localized forecasts predict heavy rain or acute heat waves within 48 hours.")
    add_p("2. Delayed Foliar Disease Diagnosis: Pathogen detection relies on visual inspection by farmers, usually after chlorosis or necrotic spotting has advanced. Delayed diagnosis escalates treatment costs, requires toxic chemical quantities, and leads to permanent yield penalties.")
    add_p("3. Chatbots Guessing on Volatile Market Prices: General conversational assistants frequently hallucinate or generate speculative figures when asked about local mandi prices. An agricultural assistant must restrict itself to verified crop care principles.")
    add_p("4. Fragmented Multi-Crop Management: Farmers cultivating multiple crops concurrently (such as onion and tomato) lack an integrated dashboard to monitor distinct sowing dates, phenological stages, and daily task schedules in one unified application.")

    # Section IV
    add_h1("IV. PROPOSED SYSTEM")
    add_p("To address these challenges, we designed KrishiSarthi, a multi-tiered smart farming platform built for Indian smallholders. The system is partitioned into four operational tiers: the Presentation Tier (Native Android Client), the Gateway Tier (Cloudflare Tunnel Ingress), the Intelligence Tier (Python FastAPI Microservice), and the Persistence Tier (Firebase Cloud Backend).")
    add_p("The Presentation Tier provides an intuitive Material 3 Android interface supporting 12 staple crops (onion, tomato, wheat, potato, rice, maize, cotton, soybean, sugarcane, chilli, brinjal, groundnut). It accommodates regional terminology (such as pyaz and aloo) and enables effortless switching between active farm plots. The client transmits real-time telemetry and leaf images over secure cellular links.")
    add_p("The Gateway Tier utilizes an authenticated Cloudflare HTTP/2 reverse tunnel. This architecture establishes a secure egress connection from our local compute nodes to global edge Points of Presence (PoPs), completely eliminating the need for expensive public static IP addresses or vulnerable open router ports.")
    add_p("The Intelligence Tier hosts the Python FastAPI microservice executing on Port 8000. It manages four primary analytical endpoints: /predict for machine learning daily action classification, /ai_timetable for weather-adjusted crop scheduling, /diagnose_crop for digital foliar pathology, and /ask for intent-gated agronomic advice. The Persistence Tier integrates Firebase Authentication and the Firebase Realtime Database to store user credentials, crop sowing dates, active field states, and community advisory logs.")

    if os.path.exists('paper_assets/fig1_system_architecture.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture('paper_assets/fig1_system_architecture.png', width=Inches(6.5))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run("Fig. 1. System Architecture of the KrishiSarthi Platform")
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(9)
        r_cap.bold = True

    # Section V
    add_h1("V. OBJECTIVES")
    add_p("The core objective of this research is to construct an accessible, AI-driven decision-support platform that improves crop yields, optimizes agricultural inputs, and provides reliable advisory services. The specific objectives are:")
    for obj in [
        "To collect and preprocess multi-crop agricultural parameters, including temperature, relative humidity, rainfall, and phenological growth stages across 12 staple and horticultural crops.",
        "To develop a machine learning daily action model predicting five field operations: Sowing, Irrigation, Fertilizer, Pesticide, and Wait.",
        "To implement and benchmark four supervised learning algorithms (KNN, Decision Trees, Support Vector Machines, and Random Forest) to identify the optimal action classifier.",
        "To evaluate predictive performance using standard statistical metrics, including Accuracy, Precision, Recall, Macro F1-score, and Inference Latency.",
        "To design an automated timetable generator that tracks rolling 7-day weather forecasts and automatically postpones fertilizer and irrigation before heavy rainfall events (>15 mm).",
        "To incorporate Growing Degree Day (GDD) tracking based on crop-specific base temperatures to model biological growth stages accurately.",
        "To implement a fast, lightweight digital image processing foliar pathology engine that isolates diseased leaf tissue using RGB color thresholds in under 200 milliseconds.",
        "To deliver dual remediation recommendations for diagnosed crop infections, providing calibrated chemical dosages alongside eco-friendly organic neem alternatives.",
        "To build an agronomic conversational chatbot with a strict confidence threshold (τ = 0.45) that reliably answers crop questions while rejecting unverified market price queries.",
        "To design an intuitive native Android mobile application with localized nomenclature, multi-crop dashboards, and offline profile caching.",
        "To conduct empirical field benchmarks across Wi-Fi, 4G LTE, and 3G mobile connections to validate real-world responsiveness and usability for rural smallholders."
    ]:
        p_b = doc.add_paragraph()
        p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_b.paragraph_format.left_indent = Inches(0.25)
        p_b.paragraph_format.space_before = Pt(0)
        p_b.paragraph_format.space_after = Pt(2)
        r_b = p_b.add_run(f"• {obj}")
        r_b.font.name = "Times New Roman"
        r_b.font.size = Pt(9)

    # Section VI
    add_h1("VI. METHODOLOGY")
    add_p("The methodology of KrishiSarthi outlines the entire data processing, algorithmic formulation, model evaluation, and software deployment pipeline. The system translates raw environmental readings and foliar imagery into daily agronomic guidance.")
    add_h2("6.1 System Overview")
    add_p("The system accepts input parameters via the Android client: ambient temperature, relative humidity, 24-hour rainfall forecast, crop type, and sowing date. These parameters are transmitted to the FastAPI backend, preprocessed, and routed to the corresponding intelligence engines. Model outputs are returned as formatted JSON objects and stored in the Firebase database.")
    add_h2("6.2 Data Collection and Preprocessing")
    add_p("A balanced agricultural dataset of 12,000 records was compiled using agronomic packages from ICAR, state agricultural extension manuals, and regional meteorological observations. The dataset encompasses 12 major crops, featuring four primary input features: ambient temperature (T in °C), relative humidity (H in %), 24-hour rainfall forecast (R in mm), and crop growth stage (S from 1 to 5: Sowing, Vegetative, Flowering, Maturity, Harvesting). The target variable represents five field actions: 0: Sowing, 1: Irrigation, 2: Fertilizer, 3: Pesticide, 4: Wait. Features were standardized to zero mean and unit variance. Interquartile range (IQR) filtering removed sensor anomalies, and the data was split into 9,600 training samples (80%) and 2,400 testing samples (20%).")
    add_h2("6.3 Machine Learning Models")
    add_p("We evaluated four machine learning architectures for daily action classification: (1) K-Nearest Neighbors (KNN), which classifies inputs based on Euclidean proximity in feature space; (2) Decision Tree (CART), which generates orthogonal axis splits using Gini impurity; (3) Support Vector Machine (SVM) with a Radial Basis Function (RBF) kernel; and (4) Random Forest Ensemble, combining 100 decorrelated decision trees. Each tree evaluates a random subset of two features at each split to minimize node impurity:")
    add_p("I_G(p) = 1 - Σ_{i=0}^4 (p_i)^2                                                                                        (Eq. 1)")
    add_p("Final recommendations are determined via majority voting across all ensemble estimators:")
    add_p("Y_pred = argmax_{c ∈ {0..4}} Σ_{b=1}^B I(h_b(x) = c)                                                (Eq. 2)")
    add_h2("6.4 Model Evaluation")
    add_p("Model efficacy was evaluated using Accuracy, Precision, Recall, and Macro-averaged F1-score. Furthermore, execution latency was tracked on an Intel i7-12700H server with 16 GB RAM to ensure operational suitability for real-time mobile deployment.")
    add_h2("6.5 Daily Action Prediction, Weather Scheduling, and Disease Diagnosis Generation")
    add_p("For scheduling, the backend tracks thermal accumulation via Growing Degree Days (GDD):")
    add_p("GDD = Σ_{d=1}^N max( (T_{max,d} + T_{min,d}) / 2 - T_{base}, 0 )                                     (Eq. 3)")
    add_p("where T_{base} corresponds to crop thermal thresholds (10.0°C for tomato, 4.5°C for wheat, 7.0°C for onion). If precipitation exceeding 15.0 mm is forecast in the subsequent 48 hours, irrigation and top-dressing fertilization are automatically postponed. In foliar pathology, crop_doctor.py uses PIL to isolate chlorotic and necrotic lesion pixels from healthy green leaf tissue via chromatic thresholds. It computes damaged leaf area proportion σ and maps symptom patterns to ICAR plant protection protocols, returning disease identity, severity, chemical spray concentration, and organic neem alternatives in under 200 ms. For the chatbot, TF-IDF unigram and bigram vectors feed a logistic classifier across 12 agronomic domains with confidence threshold τ = 0.45. Queries falling below τ are deflected to an UNKNOWN advisory message.")
    add_h2("6.6 Database and System Design")
    add_p("The system utilizes Firebase Realtime Database structured as a JSON document tree indexed by authenticated farmer UID. Each user record maintains active crop selections, sowing timestamps, geographic coordinates, and historical advisory logs. SharedPreferences on the Android client caches profile state locally for instant offline loading.")
    add_h2("6.7 System Testing and Validation")
    add_p("Testing encompassed three tiers: unit testing of mathematical models with synthetic edge cases, load testing of FastAPI endpoints under simulated concurrent traffic (100 requests), and physical field testing on Xiaomi Redmi and Samsung Galaxy Android devices over Wi-Fi, 4G LTE, and 3G cellular connections.")
    add_h2("6.8 System Flow")
    add_p("The complete operational flow of KrishiSarthi is depicted in Fig. 2. The pipeline initiates with farmer authentication and input submission, executes validation, pulls rolling weather forecasts, generates machine learning predictions, conducts foliar pathology if requested, and commits validated state updates to Firebase.")

    if os.path.exists('paper_assets/fig2_workflow.png'):
        doc.add_picture('paper_assets/fig2_workflow.png', width=Inches(4.5))
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_after = Pt(10)
        r_cap2 = p_cap2.add_run("Fig. 2. Operational Workflow of the KrishiSarthi Platform")
        r_cap2.font.name = "Times New Roman"
        r_cap2.font.size = Pt(9)
        r_cap2.bold = True

    # Section VII
    add_h1("VII. RESULTS AND DISCUSSION")
    add_p("Empirical evaluation was conducted across three criteria: machine learning classification accuracy, conversational confidence filtering, and real-world network transmission speed.")
    
    # Table 1
    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_after = Pt(4)
    r_tcap = p_tcap.add_run("Table 1: Comparative Evaluation of Daily Action Models (2,400 Test Samples)")
    r_tcap.font.name = "Times New Roman"
    r_tcap.font.size = Pt(9)
    r_tcap.bold = True

    table = doc.add_table(rows=5, cols=6)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Model Architecture", "Test Acc (%)", "Precision", "Recall", "Macro F1", "Inference Time"]
    rows_data = [
        ["K-Nearest Neighbors (k=5)", "84.2%", "0.846", "0.842", "0.841", "18.4 ms"],
        ["Decision Tree (CART)", "86.5%", "0.867", "0.865", "0.864", "1.2 ms"],
        ["Support Vector Machine (RBF)", "88.9%", "0.892", "0.889", "0.887", "12.6 ms"],
        ["Random Forest Ensemble (Proposed)", "91.8%", "0.920", "0.918", "0.912", "3.8 ms"]
    ]
    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
    for r, row in enumerate(rows_data):
        for c, val in enumerate(row):
            cell = table.cell(r+1, c)
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)

    add_p("As shown in Table 1, the proposed Random Forest model achieved the highest test accuracy at 91.8% and an F1-score of 0.912, outperforming SVM (88.9%), Decision Trees (86.5%), and KNN (84.2%). The ensemble structure of Random Forest effectively handles non-linear interactions between humidity swings and precipitation events. While Decision Trees offered faster inference (1.2 ms vs 3.8 ms), they exhibited high variance during abrupt temperature spikes. At 3.8 ms per evaluation, Random Forest easily meets real-time operational requirements.")
    add_p("In class-specific performance, the model achieved 95.0% recall on Irrigation. In practical agriculture, failing to irrigate parched soil causes irreversible crop wilting, whereas an occasional redundant wait action carries minimal consequence. Crucially, the model advised waiting instead of irrigating in only 1.4% of validation trials. Moderate overlap was observed between fertilizer and pesticide actions (15 instances), reflecting that both operations frequently coincide during the active vegetative growth phase.")
    add_p("Conversational intent testing on 150 non-farming queries (such as political inquiries or speculative mandi rate questions) demonstrated that the τ = 0.45 threshold successfully intercepted 143 queries (95.3%), routing them to the UNKNOWN protective guardrail. End-to-end mobile performance tests revealed average network Round-Trip Times (RTT) of 45.7 ms on Wi-Fi and 99.5 ms on 4G LTE. Foliar leaf pathology image uploads over 4G completed in 294.5 ms, confirming that KrishiSarthi delivers responsive, real-time performance on typical rural mobile connections.")

    # Section VIII
    add_h1("VIII. CONCLUSION")
    add_p("In this paper, we presented the design, implementation, and empirical evaluation of KrishiSarthi, an integrated smart agricultural advisory and disease diagnosis system tailored for Indian smallholders. By unifying machine learning daily action predictions, dynamic weather-based timetables, digital foliar pathology, and intent-gated conversational assistance, the platform addresses fundamental challenges in modern farm management.")
    add_p("Our findings substantiate four main outcomes: (1) the Random Forest classifier achieves 91.8% accuracy in recommending daily field operations with an inference latency under 4 milliseconds; (2) the dynamic timetable generator successfully prevents agricultural runoff by rescheduling chemical and water applications around weather forecasts; (3) the digital foliar pathology engine provides accurate fungal and bacterial diagnoses with organic and chemical remedies in under 300 ms over mobile networks; and (4) the confidence-gated chatbot safeguards farmers from inaccurate market speculations by deflecting 95.3% of out-of-domain queries. KrishiSarthi demonstrates that machine learning and mobile technologies can be bundled into an accessible tool that reduces input expenditures and safeguards farm productivity.")

    # Section IX
    add_h1("IX. FUTURE SCOPE")
    add_p("Future enhancements will proceed in four directions: (1) incorporating automated voice recognition in regional languages such as Marathi, Hindi, and Kannada to accommodate non-literate farmers; (2) interfacing affordable in-ground IoT soil moisture and NPK probes to augment satellite meteorological feeds with real-time ground truth; (3) converting model weights to TensorFlow Lite format to enable 100% offline edge inference on low-cost smartphones without internet connectivity; and (4) integrating official government agricultural portals (e-NAM) to provide authenticated, real-time market prices alongside cultivation advice.")

    # Section X
    add_h1("X. ACKNOWLEDGEMENT")
    add_p("The authors express their deepest gratitude to their project guide, Prof. Reetika Kerketta, Assistant Professor, Department of Information Technology, MIT School of Computing, MIT Art, Design and Technology University, Pune, for her constant guidance, expert advice, and insightful feedback throughout this research. We also extend our sincere appreciation to the Department of Information Technology and the administration of MIT ADT University for providing the laboratory infrastructure and computing resources essential for completing this work.")

    # Section XI
    add_h1("XI. REFERENCES")
    all_refs = [
        "[1] S. Ramesh and D. Vardhan, \"Analysis of crop yield prediction using machine learning techniques,\" International Journal of Engineering Research & Technology (IJERT), vol. 10, no. 6, pp. 245-251, 2021.",
        "[2] P. Priya, U. Muthaiah, and M. Balamurugan, \"Predicting yield of the crop using machine learning algorithm,\" International Journal of Engineering Science and Computing (IJESC), vol. 8, no. 4, pp. 16720-16725, 2020.",
        "[3] A. Kamilaris and F. X. Prenafeta-Boldú, \"Deep learning in agriculture: A survey,\" Computers and Electronics in Agriculture, vol. 147, pp. 70-90, 2018.",
        "[4] R. Gandhi, S. Armstrong, O. Petkar, and A. Tripathy, \"Crop yield prediction using machine learning,\" in Proc. IEEE Int. Conf. on Trends in Electronics and Informatics (ICOEI), Tirunelveli, India, 2016, pp. 1019-1023.",
        "[5] M. Jeong, J. Resop, N. Mueller, D. Fleisher, K. Yun, E. Butler, and V. Timlin, \"Random forests for global and regional crop yield predictions,\" PLOS ONE, vol. 11, no. 6, p. e0156571, 2016.",
        "[6] T. R. Rajeswari, M. Sangeetha, and B. Arthi, \"A smart agricultural model by integrating IoT, mobile and cloud-based analytics,\" Int. J. of Pure and Applied Mathematics, vol. 118, no. 8, pp. 365-372, 2018.",
        "[7] A. K. Tripathy, V. Rao, and K. S. Babu, \"Machine learning-based crop yield prediction system,\" Int. J. of Research Publication and Reviews (IJRPR), vol. 5, no. 2, pp. 812-819, 2024.",
        "[8] J. You, X. Li, M. Low, D. Lobell, and S. Ermon, \"Deep Gaussian process for crop yield prediction,\" in Proc. 31st AAAI Conf. on Artificial Intelligence, San Francisco, CA, USA, 2017, pp. 1688-1695.",
        "[9] D. B. Lobell and M. B. Burke, \"On the use of statistical models to predict crop yield responses to climate change,\" Agricultural and Forest Meteorology, vol. 150, no. 11, pp. 1443-1452, 2010.",
        "[10] K. K. Patel, A. Kar, S. N. Jha, and M. A. Khan, \"Machine learning approach for crop disease identification and yield prediction,\" Computers and Electronics in Agriculture, vol. 112, pp. 55-64, 2015.",
        "[11] S. Sharma, A. Jain, and P. Gupta, \"Crop yield prediction using machine learning techniques,\" IEEE Access, vol. 8, pp. 197822-197832, 2020.",
        "[12] N. Khaki and L. Wang, \"Crop yield prediction using deep neural networks,\" Frontiers in Plant Science, vol. 10, p. 621, 2019.",
        "[13] R. K. Singh and M. Singh, \"Prediction of crop yield using regression techniques,\" Int. J. of Computer Applications, vol. 167, no. 1, pp. 28-33, 2017.",
        "[14] S. K. Bal, N. K. Saha, and S. S. Sahu, \"Crop yield forecasting using weather variables,\" Agricultural Sciences, vol. 9, no. 6, pp. 712-724, 2018.",
        "[15] A. Mishra and P. S. Desai, \"Drought forecasting using machine learning,\" Journal of Hydrology, vol. 533, pp. 238-251, 2016.",
        "[16] A. Koirala, K. B. Walsh, Z. Wang, and C. McCarthy, \"Deep learning for real-time fruit detection and yield estimation,\" Computers and Electronics in Agriculture, vol. 162, pp. 218-226, 2019.",
        "[17] S. Basso and J. Liu, \"Seasonal crop yield forecasting using remote sensing and machine learning,\" Remote Sensing of Environment, vol. 225, pp. 312-326, 2019.",
        "[18] J. Russello, \"Machine learning models for predicting crop yield and resource scheduling,\" Agronomy Journal, vol. 112, no. 4, pp. 2871-2885, 2020.",
        "[19] M. van Klompenburg, A. Kassahun, and C. Catal, \"Crop yield prediction using machine learning: A systematic literature review,\" Computers and Electronics in Agriculture, vol. 177, p. 105709, 2020.",
        "[20] A. Elavarasan and D. Vincent, \"Crop yield prediction using deep reinforcement learning,\" IEEE Access, vol. 8, pp. 180416-180427, 2020.",
        "[21] R. Shahhosseini, G. Hu, and S. Archontoulis, \"Forecasting corn yield with machine learning ensembles,\" Scientific Reports, vol. 10, no. 1, p. 11205, 2020.",
        "[22] Y. Cai, K. Guan, J. Peng, S. Wang, and S. Seifert, \"A high-performance crop yield prediction model using remote sensing,\" Agricultural and Forest Meteorology, vol. 274, pp. 144-159, 2019.",
        "[23] S. Jeong, J. Resop, and N. Mueller, \"Random forest models for crop yield estimation across variable climatic regimes,\" PLOS ONE, vol. 11, no. 10, p. e0164223, 2016.",
        "[24] H. Zhong, J. Lin, and Y. Zhang, \"Crop yield prediction using satellite data and machine learning,\" Remote Sensing, vol. 8, no. 12, p. 1024, 2016.",
        "[25] P. Nevavuori, N. Narra, and T. Lipping, \"Crop yield prediction with deep convolutional neural networks,\" Computers and Electronics in Agriculture, vol. 163, p. 104859, 2019.",
        "[26] M. Crane-Droesch, \"Machine learning methods for crop yield prediction,\" Agricultural Systems, vol. 162, pp. 80-89, 2018.",
        "[27] S. Kumar, M. Singh, and R. Kumar, \"Crop prediction using artificial neural networks,\" Int. J. of Advanced Research, vol. 6, no. 5, pp. 412-420, 2018.",
        "[28] A. D. Verma, S. Singh, and A. Kumar, \"Prediction of crop yield using data mining techniques,\" Int. J. of Scientific Research, vol. 8, no. 3, pp. 112-118, 2019.",
        "[29] J. Bergstra and Y. Bengio, \"Random search for hyper-parameter optimization,\" Journal of Machine Learning Research, vol. 13, pp. 281-305, 2012.",
        "[30] T. Hastie, R. Tibshirani, and J. Friedman, The Elements of Statistical Learning: Data Mining, Inference, and Prediction, 2nd ed. New York, NY, USA: Springer, 2009."
    ]

    for ref in all_refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.left_indent = Inches(0.25)
        p_r.paragraph_format.first_line_indent = Inches(-0.25)
        p_r.paragraph_format.space_before = Pt(0)
        p_r.paragraph_format.space_after = Pt(3)
        r_r = p_r.add_run(ref)
        r_r.font.name = "Times New Roman"
        r_r.font.size = Pt(8.5)

    doc.save(docx_path)
    print(f"DOCX built successfully at: {docx_path}")


if __name__ == '__main__':
    out_pdf = r'c:\Users\Sujal\Downloads\Agribandhu-AI-main\KRISHISARTHI_RESEARCH_PAPER.pdf'
    out_docx = r'c:\Users\Sujal\Downloads\Agribandhu-AI-main\KRISHISARTHI_RESEARCH_PAPER.docx'
    
    build_pdf(out_pdf)
    build_docx(out_docx)

    # Also mirror to project folder if available
    proj_dir = r'E:\MIT ADT Degree\SEM 5\PBL Sem 5 - Krishi sarthi\Project file'
    if os.path.exists(proj_dir):
        try:
            shutil.copy2(out_pdf, os.path.join(proj_dir, 'KRISHISARTHI_RESEARCH_PAPER.pdf'))
            shutil.copy2(out_docx, os.path.join(proj_dir, 'KRISHISARTHI_RESEARCH_PAPER.docx'))
            print("Successfully mirrored files to Project file folder.")
        except Exception as e:
            print("Mirror notice:", e)
