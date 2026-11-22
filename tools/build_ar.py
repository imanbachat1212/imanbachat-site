# Builds the Arabic pages (ar/index.html, ar/pricing.html, ar/privacy.html)
# from the English pages. Run from the repo root:  python3 tools/build_ar.py
# Every replacement must match, so a changed English sentence fails loudly
# instead of leaving English text on the Arabic site.
import json, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CAL = 'https://cal.com/iman-bachat-0baopr/30min?user=iman-bachat-0baopr&amp;overlayCalendar=true'

RTL_CSS = """<style>
@font-face{font-family:'IBM Plex Sans Arabic';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/ibm-plex-sans-arabic-arabic-400-normal.woff2) format('woff2')}
@font-face{font-family:'IBM Plex Sans Arabic';font-style:normal;font-weight:500;font-display:swap;src:url(/fonts/ibm-plex-sans-arabic-arabic-500-normal.woff2) format('woff2')}
@font-face{font-family:'IBM Plex Sans Arabic';font-style:normal;font-weight:700;font-display:swap;src:url(/fonts/ibm-plex-sans-arabic-arabic-700-normal.woff2) format('woff2')}
html[dir=rtl] body,html[dir=rtl] .btn,html[dir=rtl] .chip,html[dir=rtl] .field,html[dir=rtl] .opt,html[dir=rtl] button{font-family:'Space Grotesk','IBM Plex Sans Arabic',system-ui,sans-serif}
html[dir=rtl] *{letter-spacing:0!important}
html[dir=rtl] [style*="JetBrains"]{font-family:'IBM Plex Sans Arabic',sans-serif!important;font-size:14px!important;font-weight:700}
html[dir=rtl] h1,html[dir=rtl] h2,html[dir=rtl] h3{line-height:1.3!important}
html[dir=rtl] .skip{left:auto;right:12px}
html[dir=rtl] .nav a:not(.btn)::after{transform-origin:right}
html[dir=rtl] .pick,html[dir=rtl] .logo-demo{margin-left:0;margin-right:auto}
html[dir=rtl] .logo-demo{direction:ltr}
html[dir=rtl] .ib-page__body,html[dir=rtl] .ib-chat__head>span,html[dir=rtl] .wa__msg,html[dir=rtl] .ib-logged span{direction:rtl}
html[dir=rtl] .tab{padding:0 24px 0 40px;border-radius:0 var(--r-sm) 0 0;clip-path:polygon(24px 0,100% 0,100% 100%,0 100%)}
html[dir=rtl] .band{border-radius:var(--r) 0 var(--r) var(--r)}
html[dir=rtl] .ui__sheet th{text-align:right}
html[dir=rtl] .how__list{padding-left:0;padding-right:20px}
html[dir=rtl] .opt{text-align:right}
html[dir=rtl] .result__price{direction:ltr;text-align:right}
html[dir=rtl] blockquote[lang=en]{direction:ltr;text-align:left}
.lang{font-weight:700!important;color:var(--ink)!important}
html[dir=rtl] .foot-name{line-height:1.3;padding:8px 0 32px;font-size:16vw}
</style>
"""

def rep(s, pairs, name):
    for old, new in pairs:
        if old not in s:
            sys.exit(f'[{name}] not found: {old[:90]!r}')
        s = s.replace(old, new)
    return s

def head_common(s, path, title, desc):
    url = 'https://imanbachat.com/ar/' + path
    en = 'https://imanbachat.com/' + path
    s = re.sub(r'\n<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', s)
    s = s.replace('\n<meta property="og:locale:alternate" content="ar_LB">', '')
    s = s.replace('.lang{font-weight:700!important;color:var(--ink)!important}\n', '')
    s = s.replace('<html lang="en">', '<html lang="ar" dir="rtl">', 1)
    s = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', s, count=1)
    s = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*', lambda m: m.group(1) + desc, s)
    s = re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*', lambda m: m.group(1) + title, s)
    s = re.sub(r'<link rel="canonical" href="[^"]*">',
               f'<link rel="canonical" href="{url}">\n'
               f'<link rel="alternate" hreflang="en" href="{en}">\n'
               f'<link rel="alternate" hreflang="ar" href="{url}">\n'
               f'<link rel="alternate" hreflang="x-default" href="{en}">', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', s, count=1)
    s = s.replace('<meta property="og:locale" content="en_US">', '<meta property="og:locale" content="ar_LB">\n<meta property="og:locale:alternate" content="en_US">')
    s = s.replace('content="Iman Bachat: websites that bring clients, WhatsApp AI that handles them"', 'content="Iman Bachat: مواقع تجلب العملاء، وذكاء اصطناعي على واتساب يتولّاهم"')
    s = s.replace('</head>', RTL_CSS + '</head>', 1)
    return s

def jsonld(s, graph):
    block = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    s, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">\n' + block + '\n</script>', s, count=1, flags=re.S)
    assert n == 1
    return s

FOOTER = [
    ("<h2 class=\"h2\">Talk soon. Let's build yours.</h2>", '<h2 class="h2">إلى اللقاء قريبًا. لنبنِ موقعك.</h2>'),
    ("<p>Whether it's your first website or the system behind one you already have, the first call is free.</p>", '<p>سواء كان أول موقع لك أو النظام خلف موقع لديك أصلًا، المكالمة الأولى مجانية.</p>'),
    ('>Book a free call</a>', '>احجز مكالمة مجانية</a>'),
    ('>Instagram @imanbachatt</a>', '>إنستغرام <bdi>@imanbachatt</bdi></a>'),
    ('rel="noopener">LinkedIn</a>\n      </address>', 'rel="noopener">لينكدإن</a>\n      </address>'),
    ('<span>© 2026 Iman Bachat · Tripoli, Lebanon · <a href="/privacy" style="color:inherit">Privacy</a></span><span>I build the website. Then I build the system behind it.</span>',
     '<span>© 2026 Iman Bachat · طرابلس، لبنان · <a href="/ar/privacy" style="color:inherit">الخصوصية</a></span><span>أبني الموقع، ثم أبني النظام الذي يقف خلفه.</span>'),
]

MENU_JS = [
    ("o?'Close menu':'Open menu'", "o?'أغلق القائمة':'افتح القائمة'"),
    ('aria-label="Open menu"', 'aria-label="افتح القائمة"'),
    ('aria-label="Main"', 'aria-label="القائمة الرئيسية"'),
    ('aria-label="Iman Bachat, home"', 'aria-label="Iman Bachat، الصفحة الرئيسية"'),
    ('>Skip to content</a>', '>انتقل إلى المحتوى</a>'),
]

FAQ = [
    ("كم تكلفة الموقع الإلكتروني في لبنان؟", "تعتمد على عدد الصفحات، ونوع البناء (بدون برمجة أو برمجة مخصّصة)، واللغات، ومستوى الحركة. تعطيك حاسبة الأسعار تقديرًا فوريًا، ويُثبَّت سعرك النهائي بعد مكالمة مجانية لمدة 30 دقيقة. ويحصل الموقع ومساعد واتساب الذكي معًا على خصم 10%."),
    ("كم يستغرق بناء موقع إلكتروني؟", "تستغرق صفحة الهبوط عادةً من أسبوع إلى أسبوعين، والموقع الكامل من أسبوعين إلى أربعة، ومساعد واتساب الذكي من أسبوعين إلى أربعة حسب ما يتولّاه. تعرف المدة قبل أن نبدأ."),
    ("ماذا يمكن أن يقدّم مساعد واتساب الذكي لعملي؟", "يردّ على زبائنك على واتساب ليلًا ونهارًا، ويستقبل الحجوزات والطلبات، ويسجّل كلًّا منها في جدول أو لوحة تحكم كي لا يضيع شيء. ويُجهَّز خصيصًا لعملك: مطعم، عيادة، مكتب محاماة، متجر أو خدمة."),
    ("هل أحتاج موقعًا إلكترونيًا لأستخدم مساعد واتساب الذكي؟", "لا، يعمل وحده. لكن الاثنين معًا يعطيان أفضل نتيجة: الموقع يجلب الناس، والمساعد الذكي يتولّاهم."),
    ("كم تكلفة تشغيل مساعد واتساب الذكي؟", "هناك تكاليف شهرية بسيطة للاستضافة ورسائل واتساب واستخدام الذكاء الاصطناعي. أشرحها لك في المكالمة قبل أن تلتزم."),
    ("هل سيظهر موقعي على Google؟", "كل موقع أبنيه سريع، ومتوافق مع الهاتف، ومجهّز بالأساسيات التي يبحث عنها Google. ويمكنني أيضًا إعداد ملفك التجاري على Google ليجدك الزبائن على خرائط Google."),
    ("هل تبنين مواقع لأعمال خارج لبنان؟", "نعم، لديّ عملاء في لبنان والإمارات وأستراليا وكندا. كل العمل يتمّ عن بُعد، والمكالمات في توقيتك."),
    ("كيف أدفع ثمن الموقع؟", "في لبنان عبر Whish Money أو OMT أو تحويل مصرفي، ومن الخارج عبر تحويل مصرفي أو Wise أو PayPal. يبدأ المشروع بدفعة مقدّمة 50%، ويُدفع الباقي قبل الإطلاق."),
]

# ------------------------------------------------------------------ homepage
def build_index():
    s = open('index.html').read()
    s = head_common(s, '', 'Iman Bachat — مواقع إلكترونية ومساعد واتساب الذكي',
                    'مطوّرة مواقع في طرابلس، لبنان: مواقع إلكترونية تجلب لك العملاء، ومساعد واتساب ذكي يردّ على زبائنك ويستقبل الحجوزات ويسجّل كل طلب تلقائيًا.')
    s = jsonld(s, [
        {"@type": "WebPage", "@id": "https://imanbachat.com/ar/#page", "url": "https://imanbachat.com/ar/",
         "name": "Iman Bachat — مواقع إلكترونية وذكاء اصطناعي على واتساب", "inLanguage": "ar",
         "isPartOf": {"@id": "https://imanbachat.com/#website"}, "about": {"@id": "https://imanbachat.com/#business"}},
        {"@type": "FAQPage", "@id": "https://imanbachat.com/ar/#faq", "inLanguage": "ar",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    ])
    faq_html = '\n'.join(
        f'      <details{" open" if i == 0 else ""}><summary>{q}<span aria-hidden="true">+</span></summary><p>'
        + (a.replace('حاسبة الأسعار', '<a href="/ar/pricing">حاسبة الأسعار</a>') if i == 0 else a) + '</p></details>'
        for i, (q, a) in enumerate(FAQ))
    s, n = re.subn(r'(<div class="faq__list rise d1">\n).*?(\n    </div>\n  </div>\n</section>)', lambda m: m.group(1) + faq_html + m.group(2), s, flags=re.S)
    assert n == 1
    s = rep(s, MENU_JS + FOOTER + [
        # nav
        ('<a href="#services">Services</a><a href="#work">Work</a><a href="#about">About</a><a href="#pricing">Pricing</a><a href="#faq">FAQ</a><a class="lang" href="/ar/" lang="ar" hreflang="ar">عربي</a>\n      <a class="btn btn--lime" href="#book">Book a call</a>',
         '<a href="#services">الخدمات</a><a href="#work">أعمالي</a><a href="#about">من أنا</a><a href="#pricing">الأسعار</a><a href="#faq">الأسئلة الشائعة</a><a class="lang" href="/" lang="en" hreflang="en">EN</a>\n      <a class="btn btn--lime" href="#book">احجز مكالمة</a>'),
        # hero
        ("Hi, I'm Iman.</p>", 'مرحبًا، أنا إيمان.</p>'),
        ('>Websites that bring you clients.</h1>', '>مواقع إلكترونية تجلب لك العملاء.</h1>'),
        ('>Then I build the WhatsApp AI behind them, so every message is answered, every booking confirmed and every order logged.</p>',
         '>ثم أبني خلفها مساعد واتساب الذكي، فتُجاب كل رسالة، ويُؤكَّد كل حجز، ويُسجَّل كل طلب.</p>'),
        ('<a class="btn btn--lime" href="pricing.html">Get a free estimate</a>', '<a class="btn btn--lime" href="/ar/pricing">احصل على تقدير مجاني</a>'),
        ('>See my work</a>', '>شاهد أعمالي</a>'),
        ('aria-label="Experience"', 'aria-label="الخبرة"'),
        ('<span>4+ years of experience</span><span>15+ projects delivered</span>', '<span>أكثر من 4 سنوات خبرة</span><span>أكثر من 15 مشروعًا منجزًا</span>'),
        # demo (static default = restaurant)
        ('<p class="ib-page__name" id="d-site">Shawarma House</p>', '<p class="ib-page__name" id="d-site">بيت الشاورما</p>'),
        ('>Hot shawarma, delivered in Tripoli.</p>', '>شاورما ساخنة، توصيل في طرابلس.</p>'),
        ('<span class="ib-page__btn" id="d-btn">Order on WhatsApp</span>', '<span class="ib-page__btn" id="d-btn">اطلب عبر واتساب</span>'),
        ('<b id="d-name">Shawarma House</b><small>AI assistant · online</small>', '<b id="d-name">بيت الشاورما</b><small>مساعد ذكي · متصل</small>'),
        ('id="d-in">2 shawarma and 1 fries to Mina, near the pharmacy. Cash please<span', 'id="d-in">2 شاورما و1 بطاطا إلى الميناء، قرب الصيدلية. الدفع نقدًا<span'),
        ('id="d-out">Got it! 2 shawarma + 1 fries to Mina, cash. Arriving in about 30 min.<span', 'id="d-out">تمام! 2 شاورما + 1 بطاطا إلى الميناء، نقدًا. يصل خلال 30 دقيقة تقريبًا.<span'),
        ('<span id="d-log">Logged: 2× shawarma · Mina · Cash</span>', '<span id="d-log">تم التسجيل: 2× شاورما · الميناء · نقدًا</span>'),
        ('<p id="pick-h">Pick a business and watch a new client get handled, start to finish.</p>', '<p id="pick-h">اختر نوع العمل وشاهد كيف يُخدَم عميل جديد من البداية إلى النهاية.</p>'),
        ('aria-pressed="true">Restaurant</button>', 'aria-pressed="true">مطعم</button>'),
        ('aria-pressed="false">Clinic</button>', 'aria-pressed="false">عيادة</button>'),
        ('aria-pressed="false">Law office</button>', 'aria-pressed="false">مكتب محاماة</button>'),
        ('aria-pressed="false">Shop</button>', 'aria-pressed="false">متجر</button>'),
        ('aria-label="read"', 'aria-label="مقروءة"'),
        # demo data in script
        ("restaurant:{site:'Shawarma House',url:'shawarmahouse.com',h:'Hot shawarma, delivered in Tripoli.',btn:'Order on WhatsApp',i:'2 shawarma and 1 fries to Mina, near the pharmacy. Cash please',o:'Got it! 2 shawarma + 1 fries to Mina, cash. Arriving in about 30 min.',log:'Logged: 2× shawarma · Mina · Cash'}",
         "restaurant:{site:'بيت الشاورما',url:'shawarmahouse.com',h:'شاورما ساخنة، توصيل في طرابلس.',btn:'اطلب عبر واتساب',i:'2 شاورما و1 بطاطا إلى الميناء، قرب الصيدلية. الدفع نقدًا',o:'تمام! 2 شاورما + 1 بطاطا إلى الميناء، نقدًا. يصل خلال 30 دقيقة تقريبًا.',log:'تم التسجيل: 2× شاورما · الميناء · نقدًا'}"),
        ("clinic:{site:'Smile Dental Clinic',url:'smiledental.com',h:'A brighter smile, booked in a minute.',btn:'Book on WhatsApp',i:'Hi, can I book a cleaning with Dr. Nour this Thursday afternoon?',o:'Thursday at 4:30 pm is free with Dr. Nour. Shall I book it under your name?',log:'Booked: Cleaning · Thu 4:30 pm'}",
         "clinic:{site:'عيادة سمايل لطب الأسنان',url:'smiledental.com',h:'ابتسامة أجمل، تحجزها في دقيقة.',btn:'احجز عبر واتساب',i:'مرحبًا، هل يمكنني حجز موعد تنظيف مع د. نور هذا الخميس بعد الظهر؟',o:'الخميس الساعة 4:30 عصرًا متاح مع د. نور. هل أحجزه باسمك؟',log:'تم الحجز: تنظيف · الخميس 4:30 م'}"),
        ("law:{site:'Haddad Law Office',url:'haddadlaw.com',h:'Clear legal advice, from the first call.',btn:'Ask on WhatsApp',i:'Good evening, I need advice about a rental contract. Can I meet a lawyer?',o:'Of course. Would Monday at 11:00 at the office suit you?',log:'Logged: Rental contract · Mon 11:00'}",
         "law:{site:'مكتب حداد للمحاماة',url:'haddadlaw.com',h:'استشارة قانونية واضحة من أول اتصال.',btn:'اسأل عبر واتساب',i:'مساء الخير، أحتاج استشارة بخصوص عقد إيجار. هل يمكنني مقابلة محامٍ؟',o:'بالتأكيد. هل يناسبك يوم الاثنين الساعة 11:00 في المكتب؟',log:'تم التسجيل: عقد إيجار · الاثنين 11:00'}"),
        ("shop:{site:'Rose Beauty',url:'rosebeauty.shop',h:'New in: the rose lip oil.',btn:'Order on WhatsApp',i:'Do you still have the rose lip oil? I want 2, delivery to Jounieh',o:'Yes, 2 are reserved for you. Delivery to Jounieh tomorrow. Whish or cash?',log:'Reserved: 2× lip oil · Jounieh'}",
         "shop:{site:'روز بيوتي',url:'rosebeauty.shop',h:'وصل حديثًا: زيت الشفاه بالورد.',btn:'اطلب عبر واتساب',i:'هل ما زال زيت الشفاه بالورد متوفرًا؟ أريد 2، والتوصيل إلى جونية',o:'نعم، حجزت لك 2. التوصيل إلى جونية غدًا. Whish أم نقدًا؟',log:'تم الحجز: 2× زيت شفاه · جونية'}"),
        # clients
        ('aria-label="Clients"', 'aria-label="العملاء"'),
        ('<p>Trusted by businesses like</p>', '<p>يثق بي أصحاب أعمال مثل</p>'),
        # services
        ('letter-spacing: 0.06em">SERVICES</div>', 'letter-spacing: 0.06em">الخدمات</div>'),
        (">Most businesses don't need a prettier website. They need more clients and less manual work.</h2>", '>معظم الأعمال لا تحتاج موقعًا أجمل، بل تحتاج عملاء أكثر وعملًا يدويًا أقل.</h2>'),
        ('>Websites that convert</h3>', '>مواقع تحقّق النتائج</h3>'),
        ('>Landing pages and business sites built to turn visitors into inquiries. Arabic and English.</p>', '>صفحات هبوط ومواقع أعمال مصمّمة لتحويل الزوار إلى استفسارات. بالعربية والإنجليزية.</p>'),
        ('>SEO + Google Business Profile</h3>', '>تحسين محركات البحث + ملف Google التجاري</h3>'),
        ('>Get found when people near you search for what you do, on Google Search and Maps.</p>', '>ليجدك الناس القريبون منك عندما يبحثون عمّا تقدّمه، على بحث Google وخرائطه.</p>'),
        ('>WhatsApp AI automation</h3>', '>أتمتة واتساب بالذكاء الاصطناعي</h3>'),
        ('>Replies to customers, takes bookings and orders, and logs everything to a sheet or dashboard, 24/7.</p>', '>يردّ على الزبائن، ويستقبل الحجوزات والطلبات، ويسجّل كل شيء في جدول أو لوحة تحكم، على مدار الساعة.</p>'),
        ('>Dashboards and systems</h3>', '>لوحات تحكم وأنظمة</h3>'),
        ('>See your orders, clients and numbers in one place, without copying anything by hand.</p>', '>شاهد طلباتك وعملاءك وأرقامك في مكان واحد، من دون نسخ أي شيء يدويًا.</p>'),
        ('>Not sure what you need?</span>', '>لست متأكدًا مما تحتاجه؟</span>'),
        ('>Book a call →</a>', '>احجز مكالمة ←</a>'),
        # work
        ('>Selected work</h2>', '>أعمال مختارة</h2>'),
        ('>Four real businesses, and what changed for each of them.</p>', '>أربعة أعمال حقيقية، وما الذي تغيّر لكل منها.</p>'),
        ('aria-label="The 360 Services order bot: WhatsApp messages on the left, logged orders on the right"', 'aria-label="بوت طلبات 360 Services: رسائل واتساب، والطلبات المسجّلة تلقائيًا"'),
        ('<p class="ui__h">360 Services orders · group</p>', '<p class="ui__h">طلبات 360 Services · مجموعة</p>'),
        ('>2 shawarma + fries, Mina near pharmacy, cash<small>Customer · 21:04</small>', '>2 شاورما + بطاطا، الميناء قرب الصيدلية، نقدًا<small>زبون · 21:04</small>'),
        ('>1 large pizza margherita, Dam w Farez bldg 4, Whish<small>Customer · 21:05</small>', '>1 بيتزا مارغريتا كبيرة، ضم وفرز مبنى 4، Whish<small>زبون · 21:05</small>'),
        ('>Same as yesterday pls, Abou Samra<small>Customer · 21:07</small>', '>نفس طلب الأمس من فضلك، أبي سمرا<small>زبون · 21:07</small>'),
        ('<p class="ui__h">Order log</p>', '<p class="ui__h">سجل الطلبات</p>'),
        ('<caption class="vh">Orders logged automatically from WhatsApp</caption>', '<caption class="vh">طلبات تُسجَّل تلقائيًا من واتساب</caption>'),
        ('<th>Time</th><th>Area</th><th>Pay</th><th>Status</th>', '<th>الوقت</th><th>المنطقة</th><th>الدفع</th><th>الحالة</th>'),
        ('<td>Mina</td><td>Cash</td><td class="ui__ok">Logged</td>', '<td>الميناء</td><td>نقدًا</td><td class="ui__ok">مسجّل</td>'),
        ('<td>Dam w Farez</td><td>Whish</td><td class="ui__ok">Logged</td>', '<td>ضم وفرز</td><td>Whish</td><td class="ui__ok">مسجّل</td>'),
        ('<td>Abou Samra</td><td>Cash</td><td>Check</td>', '<td>أبي سمرا</td><td>نقدًا</td><td>للمراجعة</td>'),
        ('<h3>No more lost orders</h3>', '<h3>لا طلبات ضائعة بعد اليوم</h3>'),
        ('>Delivery company · WhatsApp AI</p>', '>شركة توصيل · ذكاء اصطناعي على واتساب</p>'),
        ('>80–90% of manual order handling, automated.</p>', '>أتمتة 80–90% من معالجة الطلبات اليدوية.</p>'),
        ('<p>Orders arrived in a busy WhatsApp group and the call center copied each one by hand. I built an AI that reads every message, logs the order with its area and payment, and flags anything unclear for a person.</p>',
         '<p>كانت الطلبات تصل إلى مجموعة واتساب مزدحمة، وكان مركز الاتصال ينسخ كل طلب يدويًا. بنيت ذكاءً اصطناعيًا يقرأ كل رسالة، ويسجّل الطلب مع المنطقة وطريقة الدفع، وينبّه موظفًا إلى أي طلب غير واضح.</p>'),
        ('>Want this? Book a call</a>', '>تريد هذا؟ احجز مكالمة</a>'),
        ('src="img/', 'src="/img/'),
        ('alt="Kings Entertainment Group homepage: a Zaffe procession at a wedding"', 'alt="الصفحة الرئيسية لموقع Kings Entertainment Group: موكب زفّة في حفل زفاف"'),
        ('<h3>Booked from the first screen</h3>', '<h3>حجوزات من الشاشة الأولى</h3>'),
        ('>Events · Australia</p>', '>مناسبات · أستراليا</p>'),
        ('<p>A Lebanese Zaffe and Dabke group performing at weddings across Australia. The site leads with the show and puts the reservation form one tap away, with SEO and a Google Business Profile so couples find them.</p>',
         '<p>فرقة زفّة ودبكة لبنانية تحيي حفلات الزفاف في أنحاء أستراليا. يبدأ الموقع بالعرض ويضع نموذج الحجز على بُعد نقرة واحدة، مع تحسين لمحركات البحث وملف Google التجاري ليجدها العرسان.</p>'),
        ('alt="The events gallery on the Kings site"', 'alt="معرض المناسبات في موقع Kings"'),
        ('>Visit the Kings Entertainment site</a>', '>زيارة موقع Kings Entertainment</a>'),
        ('alt="Ichrakieh law office homepage in Arabic"', 'alt="الصفحة الرئيسية لمكتب Ichrakieh للمحاماة بالعربية"'),
        ('<h3>Trust, in two languages</h3>', '<h3>ثقة بلغتين</h3>'),
        ('>Law · Tripoli</p>', '>محاماة · طرابلس</p>'),
        ('<p>A law office established in 1965. Arabic first with an English version, practice areas set out plainly, and a direct way to request a consultation by phone or WhatsApp.</p>',
         '<p>مكتب محاماة تأسّس عام 1965. العربية أولًا مع نسخة إنجليزية، ومجالات العمل معروضة بوضوح، وطريقة مباشرة لطلب استشارة عبر الهاتف أو واتساب.</p>'),
        ('>Visit the Ichrakieh Law Office site</a>', '>زيارة موقع مكتب Ichrakieh للمحاماة</a>'),
        ('alt="Farah Salhab\'s homepage: Gender and Inclusion Expert"', 'alt="الصفحة الرئيسية لموقع Farah Salhab: خبيرة في النوع الاجتماعي والشمول"'),
        ('<h3>A brand that wins work</h3>', '<h3>علامة شخصية تجلب العمل</h3>'),
        ('>Consultant · MENA</p>', '>استشارات · الشرق الأوسط وشمال أفريقيا</p>'),
        ('<p>A gender and inclusion consultant working with UN agencies. I redesigned her site around her expertise and track record, with SEO for her name and field. Another client later found me through it.</p>',
         '<p>مستشارة في النوع الاجتماعي والشمول تعمل مع وكالات الأمم المتحدة. أعدت تصميم موقعها حول خبرتها وسجلّ إنجازاتها، مع تحسين محركات البحث لاسمها ومجالها. ولاحقًا وجدني عميل آخر من خلاله.</p>'),
        ('alt="The about section of Farah Salhab\'s site"', 'alt="قسم «من أنا» في موقع Farah Salhab"'),
        (">Visit Farah Salhab's site</a>", '>زيارة موقع Farah Salhab</a>'),
        # testimonials (quotes stay in the clients' own words)
        ('>What clients say</h2>', '>ماذا يقول العملاء</h2>'),
        ('>In their own words, after launch.</p>', '>بكلماتهم كما كتبوها، بعد إطلاق مواقعهم.</p>'),
        ('<blockquote>“I had', '<blockquote lang="en">“I had'),
        ('<blockquote>“Thank you', '<blockquote lang="en">“Thank you'),
        ('<span>Sydney, Australia</span>', '<span>سيدني، أستراليا</span>'),
        ('>See their site</a>', '>شاهد موقعهم</a>'),
        ('<span>Gender &amp; Inclusion Strategist · Beirut, Lebanon &amp; International</span>', '<span>استراتيجية في النوع الاجتماعي والشمول · بيروت، لبنان ودوليًا</span>'),
        ('>See her site</a>', '>شاهد موقعها</a>'),
        # about
        ('letter-spacing: 0.06em">ABOUT</div>', 'letter-spacing: 0.06em">من أنا</div>'),
        ('>I build the website. Then I build the system behind it.</h2>', '>أبني الموقع، ثم أبني النظام الذي يقف خلفه.</h2>'),
        ("<p style=\"margin: 0\">I'm Iman, a full-stack developer and automation builder based in Lebanon, working with clients worldwide.</p>",
         '<p style="margin: 0">أنا إيمان، مطوّرة Full-stack ومُصمِّمة أنظمة أتمتة، مقيمة في لبنان وأعمل مع عملاء حول العالم.</p>'),
        ("<p style=\"margin: 0\">Before freelancing, I ran operations for a delivery company: HR, finance, orders and the call center. So I don't just build websites. I understand how a business actually runs behind them, and I build the systems that make it run with less effort.</p>",
         '<p style="margin: 0">قبل العمل المستقل، أدرت العمليات في شركة توصيل: الموارد البشرية والمالية والطلبات ومركز الاتصال. لذلك لا أبني المواقع فقط، بل أفهم كيف يعمل العمل فعليًا خلفها، وأبني الأنظمة التي تجعله يسير بجهد أقل.</p>'),
        ('>Automated lead capture</span>', '>التقاط العملاء المحتملين تلقائيًا</span>'),
        ('>WhatsApp booking &amp; order systems</span>', '>أنظمة الحجز والطلبات على واتساب</span>'),
        ('>Arabic + English websites</span>', '>مواقع بالعربية والإنجليزية</span>'),
        ('>Dashboards &amp; reporting</span>', '>لوحات تحكم وتقارير</span>'),
        ('>Found on Google &amp; Maps</span>', '>الظهور على Google والخرائط</span>'),
        (">Master's in Computer &amp; Communication Engineering</span>", '>ماجستير في هندسة الحاسوب والاتصالات</span>'),
        (">Let's talk about your business →</a>", '>لنتحدث عن عملك ←</a>'),
        # pricing teaser
        ('letter-spacing: 0.06em">PRICING</div>', 'letter-spacing: 0.06em">الأسعار</div>'),
        ('>How much will your project cost?</h2>', '>كم سيكلّف مشروعك؟</h2>'),
        ('>Pick what you need in the price calculator and get an instant estimate. No email required.</p>', '>اختر ما تحتاجه في حاسبة الأسعار واحصل على تقدير فوري. لا حاجة إلى بريد إلكتروني.</p>'),
        ('<a class="ib-btn" href="pricing.html"', '<a class="ib-btn" href="/ar/pricing"'),
        ('>Open price calculator →</a>', '>افتح حاسبة الأسعار ←</a>'),
        ('border: 1.5px solid #0E1116">Book a call</a>', 'border: 1.5px solid #0E1116">احجز مكالمة</a>'),
        # book
        ('letter-spacing: 0.06em">BOOK A CALL</div>', 'letter-spacing: 0.06em">احجز مكالمة</div>'),
        (">Let's grab a (virtual) coffee</h2>", '>لنشرب قهوة (افتراضية) معًا</h2>'),
        (">Building a website shouldn't be stressful. Book a free 1-on-1 call and tell me about your business. I'll answer your questions about design, automation and pricing, and we'll see if we're the right fit. No pressure, just honest advice.</p>",
         '>بناء موقع إلكتروني لا يجب أن يكون مرهقًا. احجز مكالمة فردية مجانية وأخبرني عن عملك. سأجيب عن أسئلتك حول التصميم والأتمتة والأسعار، ونرى إن كنا مناسبين لبعضنا. بلا ضغط، فقط نصيحة صادقة.</p>'),
        ('</span>Free call (30 min)</li>', '</span>مكالمة مجانية (30 دقيقة)</li>'),
        ('</span>Plan + fixed quote</li>', '</span>خطة + عرض سعر ثابت</li>'),
        ('</span>Build, with progress updates</li>', '</span>التنفيذ، مع تحديثات مستمرة</li>'),
        ('</span>Launch + support</li>', '</span>الإطلاق + الدعم</li>'),
        ('>Free 30-minute call</div>', '>مكالمة مجانية لمدة 30 دقيقة</div>'),
        (">Pick a time that works for you. You'll get a calendar invite with the call link.</div>", '>اختر الوقت الذي يناسبك، وستصلك دعوة في التقويم مع رابط المكالمة.</div>'),
        ('>Pick a time →</a>', '>اختر موعدًا ←</a>'),
        # faq heading
        ('>Questions you might have</h2>', '>أسئلة قد تخطر لك</h2>'),
        ('Something else? <a href="#book">Ask me on a free call</a>.', 'سؤال آخر؟ <a href="#book">اسألني في مكالمة مجانية</a>.'),
    ], 'index')
    s = rep(s, [
        ('<li>360 Services</li>', '<li><bdi>360 Services</bdi></li>'),
        ('<div class="tab">360 Services</div>', '<div class="tab"><bdi>360 Services</bdi></div>'),
        ('<p class="ui__h">طلبات 360 Services · مجموعة</p>', '<p class="ui__h">طلبات <bdi>360 Services</bdi> · مجموعة</p>'),
    ], 'index-bidi')
    leftover = [w for w in ['Book a call', 'Services</a>', 'Learn more', 'Get a free', ' Selected'] if w in s]
    assert not leftover, leftover
    return s

# ------------------------------------------------------------------ pricing
def build_pricing():
    s = open('pricing.html').read()
    s = head_common(s, 'pricing', 'حاسبة أسعار المواقع ومساعد واتساب الذكي — Iman Bachat',
                    'احصل على تقدير فوري لسعر موقعك الإلكتروني أو مساعد واتساب الذكي أو كليهما. اختر عدد الصفحات واللغات والإضافات لترى التكلفة ومدة التنفيذ مباشرة.')
    s = jsonld(s, [
        {"@type": "WebPage", "@id": "https://imanbachat.com/ar/pricing#page", "url": "https://imanbachat.com/ar/pricing",
         "name": "حاسبة أسعار المواقع ومساعد واتساب الذكي — Iman Bachat", "inLanguage": "ar",
         "isPartOf": {"@id": "https://imanbachat.com/#website"}, "about": {"@id": "https://imanbachat.com/#business"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": "https://imanbachat.com/ar/"},
            {"@type": "ListItem", "position": 2, "name": "الأسعار", "item": "https://imanbachat.com/ar/pricing"}]},
    ])
    s = rep(s, MENU_JS + FOOTER + [
        ('<a class="mark" href="index.html"', '<a class="mark" href="/ar/"'),
        ('<a href="index.html#services">Services</a><a href="index.html#work">Work</a><a href="index.html#about">About</a><a href="pricing.html" aria-current="page" style="color:#0E1116">Pricing</a><a href="index.html#faq">FAQ</a><a class="lang" href="/ar/pricing" lang="ar" hreflang="ar">عربي</a>',
         '<a href="/ar/#services">الخدمات</a><a href="/ar/#work">أعمالي</a><a href="/ar/#about">من أنا</a><a href="/ar/pricing" aria-current="page" style="color:#0E1116">الأسعار</a><a href="/ar/#faq">الأسئلة الشائعة</a><a class="lang" href="/pricing" lang="en" hreflang="en">EN</a>'),
        ('rel="noopener">Book a call</a>\n    </nav>', 'rel="noopener">احجز مكالمة</a>\n    </nav>'),
        ('>Estimate your project</h1>', '>قدّر تكلفة مشروعك</h1>'),
        ('>Pick what you need and get an instant estimate. No email required.</p>', '>اختر ما تحتاجه واحصل على تقدير فوري. لا حاجة إلى بريد إلكتروني.</p>'),
        ('>How pricing works</h2>', '>كيف تُحسب الأسعار</h2>'),
        ('<li><b>Websites</b> are priced by the number of pages, the build type (no-code or custom-coded), languages and animation level.</li>',
         '<li><b>المواقع</b> تُسعَّر حسب عدد الصفحات، ونوع البناء (بدون برمجة أو برمجة مخصّصة)، واللغات، ومستوى الحركة.</li>'),
        ('<li><b>Online stores</b> start at $900 and <b>dashboards</b> at $1,200, then adjust for languages and, for stores, build type and animation.</li>',
         '<li><b>المتجر الإلكتروني</b> يبدأ من $900، و<b>لوحة التحكم</b> من $1,200، ثم يتغيّر السعر حسب اللغات، وحسب نوع البناء ومستوى الحركة للمتجر.</li>'),
        ('<li><b>WhatsApp AI</b> is priced by what it handles: smart replies, bookings and orders, or a full system with a dashboard.</li>',
         '<li><b>مساعد واتساب الذكي</b> يُسعَّر حسب ما يتولّاه: ردود ذكية، أو حجوزات وطلبات، أو نظام كامل مع لوحة تحكم.</li>'),
        ('<li><b>Website + WhatsApp AI together</b> get a 10% bundle discount.</li>', '<li><b>الموقع ومساعد واتساب الذكي معًا</b> يحصلان على خصم 10%.</li>'),
        ('<li><b>Monthly support</b> is optional and covers hosting, small edits and keeping an eye on the AI.</li>', '<li><b>الدعم الشهري</b> اختياري، ويشمل الاستضافة والتعديلات البسيطة ومتابعة المساعد الذكي.</li>'),
        ('<li>The estimate is a range. Your exact price and timeline are confirmed after a free 30-minute call.</li>', '<li>التقدير عبارة عن نطاق سعري. يُثبَّت سعرك النهائي ومدة التنفيذ بعد مكالمة مجانية لمدة 30 دقيقة.</li>'),
        ('<i></i>LIVE ESTIMATE</p>', '<i></i>تقدير مباشر</p>'),
        ('<small>Estimated price</small>', '<small>السعر التقديري</small>'),
        ('<small>Delivery</small>', '<small>مدة التنفيذ</small>'),
        ('<small>Monthly</small>', '<small>شهريًا</small>'),
        ('rel="noopener">Book a call to confirm</a>', 'rel="noopener">احجز مكالمة لتأكيد السعر</a>'),
        ('>Final price is confirmed after a free call. Every business is different.</p>', '>يُثبَّت السعر النهائي بعد مكالمة مجانية، فكل عمل مختلف.</p>'),
        # calculator labels
        ("{key:'service',t:'1. What do you need?',o:[['web','Website','Portfolio, business site or landing page'],['store','Online store','Products, cart and orders'],['dash','Dashboard','Orders, clients and numbers in one place'],['wa','WhatsApp AI','Automate replies + orders'],['both','Website + WhatsApp AI','Best results · save 10%']]}",
         "{key:'service',t:'1. ماذا تحتاج؟',o:[['web','موقع إلكتروني','موقع شخصي أو موقع أعمال أو صفحة هبوط'],['store','متجر إلكتروني','منتجات وسلة مشتريات وطلبات'],['dash','لوحة تحكم','الطلبات والعملاء والأرقام في مكان واحد'],['wa','مساعد واتساب الذكي','أتمتة الردود والطلبات'],['both','موقع + مساعد واتساب الذكي','أفضل نتيجة · وفّر 10%']]}"),
        ("{key:'pages',t:'2. Number of pages',web:1,o:[['landing','Landing page'],['p3','3 pages'],['p5','5 pages'],['p5plus','5+ pages']]}",
         "{key:'pages',t:'2. عدد الصفحات',web:1,o:[['landing','صفحة هبوط'],['p3','3 صفحات'],['p5','5 صفحات'],['p5plus','أكثر من 5 صفحات']]}"),
        ("{key:'langs',t:'3. Languages',o:[['l1','1 language','Arabic or English'],['l2','2 languages','Arabic + English'],['l3','3 languages','e.g. + French']]}",
         "{key:'langs',t:'3. اللغات',o:[['l1','لغة واحدة','العربية أو الإنجليزية'],['l2','لغتان','العربية + الإنجليزية'],['l3','3 لغات','مثلًا + الفرنسية']]}"),
        ("{key:'build',t:'4. Build type',site:1,o:[['wp','No-code','Easy for you to edit yourself'],['code','Custom-coded','Faster and fully custom']]}",
         "{key:'build',t:'4. نوع البناء',site:1,o:[['wp','بدون برمجة','سهل التعديل بنفسك'],['code','برمجة مخصّصة','أسرع ومخصّص بالكامل']]}"),
        ("{key:'anim',t:'Animation level',site:1,o:[['none','No animation'],['light','Light'],['medium','Medium'],['heavy','Heavy']]}",
         "{key:'anim',t:'مستوى الحركة',site:1,o:[['none','بدون حركة'],['light','خفيفة'],['medium','متوسطة'],['heavy','كثيفة']]}"),
        ("{key:'addons',multi:1,site:1,t:'5. Add-ons',o:[['seo','SEO setup','+$150'],['gbp','Google Business Profile','+$60']]}",
         "{key:'addons',multi:1,site:1,t:'5. الإضافات',o:[['seo','تحسين محركات البحث','+$150'],['gbp','ملف Google التجاري','+$60']]}"),
        ("{key:'wa',t:'6. WhatsApp AI level',wa:1,o:[['replies','Smart replies','FAQs, prices, opening hours'],['orders','Bookings / orders','Takes them and logs to a sheet'],['full','Full system','Everything + dashboard + reports']]}",
         "{key:'wa',t:'6. مستوى مساعد واتساب الذكي',wa:1,o:[['replies','ردود ذكية','الأسئلة الشائعة، الأسعار، ساعات العمل'],['orders','حجوزات / طلبات','يستقبلها ويسجّلها في جدول'],['full','نظام كامل','كل ما سبق + لوحة تحكم + تقارير']]}"),
        ("{key:'support',t:'7. Monthly support',o:[['none','None','I will manage it'],['basic','Basic','Hosting + small edits · $30/mo'],['full','Full','Edits + AI monitoring · $80/mo']]}",
         "{key:'support',t:'7. الدعم الشهري',o:[['none','بدون','سأديره بنفسي'],['basic','أساسي','استضافة + تعديلات بسيطة · $30 شهريًا'],['full','كامل','تعديلات + متابعة المساعد الذكي · $80 شهريًا']]}"),
        ("' <span>(pick any)</span>'", "' <span>(اختر ما تشاء)</span>'"),
        ("if(!s.service)need.push('what you need');", "if(!s.service)need.push('ما تحتاجه');"),
        ("if(web&&!s.pages)need.push('number of pages');if(site){if(!s.build)need.push('build type');if(!s.anim)need.push('animation level')}",
         "if(web&&!s.pages)need.push('عدد الصفحات');if(site){if(!s.build)need.push('نوع البناء');if(!s.anim)need.push('مستوى الحركة')}"),
        ("if(s.service&&!s.langs)need.push('languages');", "if(s.service&&!s.langs)need.push('اللغات');"),
        ("if(s.service&&wa&&!s.wa)need.push('WhatsApp AI level');", "if(s.service&&wa&&!s.wa)need.push('مستوى مساعد واتساب الذكي');"),
        ("rm.textContent=mo?'$'+mo+'/mo':'—';\n      rs.textContent='Choose '+need.join(', ')+' to see your estimate.';",
         "rm.textContent=mo?'$'+mo+' شهريًا':'—';\n      rs.textContent='اختر '+need.join('، ')+' لترى التقدير.';"),
        ("rb.textContent=bundle?'Includes 10% bundle discount':'';", "rb.textContent=bundle?'يشمل خصم 10% على الباقة':'';"),
        ("rd.textContent=a+'–'+b+' weeks';", "rd.textContent='من '+a+' إلى '+b+' أسابيع';"),
        ("rm.textContent=mo?'$'+mo+'/mo':'—';\n    var lab", "rm.textContent=mo?'$'+mo+' شهريًا':'—';\n    var lab"),
        ("if(web)parts.push(lab('pages'));if(site){parts.push(lab('build'),lab('anim')+' animation')}", "if(web)parts.push(lab('pages'));if(site){parts.push(lab('build'),'الحركة: '+lab('anim'))}"),
        ("if(wa)parts.push('AI: '+lab('wa'))", "if(wa)parts.push('المساعد الذكي: '+lab('wa'))"),
        ("if(names.length)parts.push(names.join(', '));if(mo)parts.push(lab('support')+' support');", "if(names.length)parts.push(names.join('، '));if(mo)parts.push('الدعم: '+lab('support'));"),
    ], 'pricing')
    return s

# ------------------------------------------------------------------ privacy
def build_privacy():
    s = open('privacy.html').read()
    s = head_common(s, 'privacy', 'سياسة الخصوصية وحماية البيانات — Iman Bachat',
                    'كيف يتعامل موقع imanbachat.com مع بياناتك: لا ملفات تعريف ارتباط، ولا تتبّع، ولا إعلانات، وماذا يحدث عندما تحجز مكالمة أو تتواصل مع إيمان.')
    s = jsonld(s, [
        {"@type": "WebPage", "@id": "https://imanbachat.com/ar/privacy#page", "url": "https://imanbachat.com/ar/privacy",
         "name": "سياسة الخصوصية — Iman Bachat", "inLanguage": "ar", "isPartOf": {"@id": "https://imanbachat.com/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": "https://imanbachat.com/ar/"},
            {"@type": "ListItem", "position": 2, "name": "سياسة الخصوصية", "item": "https://imanbachat.com/ar/privacy"}]},
    ])
    s, n = re.subn(r'<main id="main">.*?</main>', lambda m: '''<main id="main">
<h1>سياسة الخصوصية</h1>
<p class="muted">آخر تحديث <time datetime="2026-11-21">21 نوفمبر 2026</time> · Iman Bachat</p>
<p>هذا الموقع، imanbachat.com، يعود إلى Iman Bachat، مطوّرة مواقع في طرابلس، لبنان. إنه موقع بسيط لعرض الأعمال، ويجمع أقل قدر ممكن من البيانات.</p>
<h2>ما الذي يجمعه هذا الموقع</h2>
<p>لا شيء يحدّد هويتك. لا حسابات، ولا ملفات تعريف ارتباط (كوكيز)، ولا أدوات تحليل، ولا أدوات تتبّع إعلانية. تعمل حاسبة الأسعار داخل متصفحك ولا ترسل اختياراتك إلى أي مكان.</p>
<h2>خدمات الأطراف الثالثة</h2>
<p><b>الاستضافة:</b> الموقع مستضاف على Netlify، التي تحتفظ بسجلات خادم عادية (مثل عنوان IP ونوع المتصفح) لأغراض الأمان والموثوقية.<br><b>الخطوط:</b> الخطوط مستضافة على هذا الموقع نفسه، فلا يرى أي طرف ثالث زيارتك بسببها.<br><b>حجز مكالمة:</b> أزرار «احجز مكالمة» تفتح موقع Cal.com. أي معلومات تُدخلها هناك تخضع <a href="https://cal.com/privacy" target="_blank" rel="noopener">لسياسة خصوصية Cal.com</a>، ولا تُشارَك معي إلا لترتيب المكالمة.</p>
<h2>إذا تواصلت معي</h2>
<p>عندما تراسلني عبر البريد الإلكتروني أو تحجز مكالمة، أستخدم اسمك وبيانات التواصل ورسالتك فقط للردّ عليك ومناقشة مشروعك. لا أبيعها ولا أشاركها، وأحذفها عند الطلب.</p>
<h2>حقوقك وأسئلتك</h2>
<p>لتعرف ما الذي أحتفظ به عنك، أو لطلب حذفه، استخدم رابط البريد الإلكتروني في أسفل <a href="/ar/">الصفحة الرئيسية</a>.</p>
</main>''', s, count=1, flags=re.S)
    assert n == 1
    s = rep(s, [
        ('<a class="back" href="/">', '<a class="back" href="/ar/">'),
        ('>Skip to content</a>', '>انتقل إلى المحتوى</a>'),
        ('<nav aria-label="Main"><a href="/">Home</a><a href="/#about">About</a><a href="/pricing">Pricing</a><a href="/#book">Contact</a><a class="lang" href="/ar/privacy" lang="ar" hreflang="ar">عربي</a></nav>',
         '<nav aria-label="القائمة الرئيسية"><a href="/ar/">الرئيسية</a><a href="/ar/#about">من أنا</a><a href="/ar/pricing">الأسعار</a><a href="/ar/#book">تواصل</a><a class="lang" href="/privacy" lang="en" hreflang="en">EN</a></nav>'),
        ('<p>© 2026 Iman Bachat · Tripoli, Lebanon · <a href="https://www.instagram.com/imanbachatt" target="_blank" rel="noopener">Instagram</a> · <a href="https://www.linkedin.com/in/iman-bachat" target="_blank" rel="noopener">LinkedIn</a></p>',
         '<p>© 2026 Iman Bachat · طرابلس، لبنان · <a href="https://www.instagram.com/imanbachatt" target="_blank" rel="noopener">إنستغرام</a> · <a href="https://www.linkedin.com/in/iman-bachat" target="_blank" rel="noopener">لينكدإن</a></p>'),
    ], 'privacy')
    return s

NAME_AR = 'إيمان باشات'
def arabic_name(s):
    # Her name in Arabic everywhere on the Arabic pages, except inside the
    # clients' English testimonials.
    keep = re.findall(r'<blockquote lang="en">.*?</blockquote>', s, re.S)
    for i, k in enumerate(keep):
        s = s.replace(k, f'@@KEEP{i}@@')
    s = s.replace('<b>Iman</b> Bachat', f'<b>إيمان</b> باشات').replace('Iman Bachat', NAME_AR)
    for i, k in enumerate(keep):
        s = s.replace(f'@@KEEP{i}@@', k)
    return s

if __name__ == '__main__':
    os.makedirs('ar', exist_ok=True)
    for name, fn in [('index.html', build_index), ('pricing.html', build_pricing), ('privacy.html', build_privacy)]:
        out = fn()
        out = arabic_name(out)
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S):
            json.loads(b)
        open(os.path.join('ar', name), 'w').write(out)
        print('built ar/' + name)
