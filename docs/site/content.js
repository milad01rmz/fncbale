/* Curated bilingual guides. All Python examples target the public fncbale API. */
(() => {
  const t=(fa,en)=>({fa,en});
  const p=(fa,en)=>({type:'p',text:t(fa,en)});
  const code=(source,label='Python',language='python')=>({type:'code',source,label,language});
  const note=(titleFa,titleEn,fa,en,tone='info')=>({type:'note',title:t(titleFa,titleEn),text:t(fa,en),tone});
  const table=(headers,rows)=>({type:'table',headers,rows});
  const section=(id,fa,en,blocks)=>({id,title:t(fa,en),blocks});
  const cards=(items)=>({type:'cards',items});
  const step=(items)=>({type:'steps',items});
  const card=(route,fa,en,bodyFa,bodyEn,icon)=>({route,title:t(fa,en),text:t(bodyFa,bodyEn),icon});
  const pages=[
    {id:'overview',group:'start',icon:'layers',title:t('یک شروع روشن','A clear starting point'),nav:t('معرفی','Overview'),summary:t('کتابخانهٔ مستقل و async برای حساب کاربری بله؛ از اولین پیام تا آلبوم، eventها و عملیات قابل‌پیگیری.','An independent async Python client for Bale user accounts. Send messages and albums, receive events, and keep delivery outcomes traceable.'),tags:['Python 3.12+','asyncio','MIT','0.1.36 alpha'],sections:[
      section('start-here','از کجا شروع کنم؟','Where should I start?',[
        cards([card('installation','نصب و اولین اجرا','Install and run','محیط Python را آماده کن و کتابخانه را نصب کن.','Set up Python and install the package.','terminal'),card('authentication','ورود و نشست','Login and sessions','یک بار وارد شو؛ دفعات بعد همان session را استفاده کن.','Sign in once; reuse the saved session next time.','key'),card('chat-id','گرفتن چت‌آیدی','Find a chat ID','username را به یک Peer معتبر تبدیل کن.','Resolve a username to a usable Peer.','target'),card('messages','اولین پیام','Your first message','متن، بولد، reply، ویرایش و حذف.','Text, bold, replies, edits, and deletions.','message')]),
        note('وضعیت نسخه','Release status','نسخهٔ فعلی alpha قابل‌استفاده است. ارسال، مدیا، آلبوم و eventهای هسته آزموده شده‌اند؛ قابلیت‌های آزمایشی در بخش پشتیبانی مشخص‌اند.','The current version is a usable alpha. Core messaging, media, albums, and events have acceptance coverage; experimental features are identified in the support guide.')
      ]),
      section('layers','چهار لایه، یک Client','Four layers, one Client',[
        {type:'layers',title:t('مسیر یک عملیات','An operation’s path'),items:[t('API شما','Your API'),t('ثبت پایدار','Durable acceptance'),t('ارسال و بازیابی','Transport & recovery'),t('نتیجه و رویداد','Result & events')],labels:['Client / Peer / Media','SQLite · outbox / inbox','WebSocket → HTTP','Message / Event / Operation']},
        p('API ساده است؛ جزئیات اتصال و صف در هسته مدیریت می‌شوند. پذیرش پایدار بعد از commit اعلام می‌شود. نتیجهٔ نامطمئن حذف نمی‌شود و شناسهٔ قابل‌پیگیری دارد.','The API stays small while the core manages connections and queues. Durable acceptance is reported after commit. An uncertain outcome remains stored with an operation ID.'),
        p('این SDK برای حساب کاربری است. Bot API، تماس و عملیات مالی در این نسخه پوشش داده نمی‌شوند. هیچ SDK دیگر بله وابستگی اجرایی آن نیست.','This SDK is for user accounts. Bot API, calls, and financial operations are outside this version. No other Bale SDK is a runtime dependency.')
      ]),
      section('working-example','یک مثال کوتاه','A small example',[
        code(`import asyncio
from fncbale import Client

async def main():
    # Create account.session first: see Login and sessions.
    async with Client("account.session", data_dir=".fncbale/app") as client:
        peer = await client.resolve_peer("@yourchannel")
        message = await client.send_message(peer, "Hello from fncbale")
        print(message.rid, message.rpc_confirmed)

asyncio.run(main())`,'app.py'),
        p('همهٔ مثال‌های دارای await باید در یک تابع async و پس از اتصال اجرا شوند. فایل‌های نمونهٔ مخزن نیز در دسترس‌اند.','Run examples containing await inside an async function after connecting. Runnable examples are also included in the repository.')
      ])
    ]},
    {id:'installation',group:'start',icon:'terminal',title:t('نصب و راه‌اندازی','Installation'),summary:t('Python 3.12 یا جدیدتر؛ نصب از مخزن عمومی یا فایل wheel، روی Windows و Linux.','Python 3.12 or newer. Install from the public repository or a release wheel on Windows and Linux.'),sections:[
      section('requirements','پیش‌نیازها','Requirements',[
        table([t('مورد','Requirement'),t('توضیح','Details')],[[t('Python','Python'),t('۳.۱۲ یا جدیدتر؛ از python --version بررسی کن.','3.12 or newer; check with python --version.')],[t('حساب بله','Bale account'),t('شمارهٔ حساب و دسترسی به کد ورود. توکن bot لازم نیست.','An account phone number and access to its login code. No bot token is required.')],[t('فضای ذخیره','Local storage'),t('برای session، صف پایدار و فایل‌های آمادهٔ ارسال.','For the session, durable queues, and prepared media files.')]]),
        p('وابستگی‌های عمومی شبکه، protobuf و مدیا با pip نصب می‌شوند. مسیر metadata از Pillow و PyAV استفاده می‌کند؛ FFmpeg CLI جداگانه لازم نیست.','pip installs the generic networking, protobuf, and media dependencies. Metadata uses Pillow and PyAV; a separate FFmpeg command-line installation is not required.')
      ]),
      section('install','نصب از GitHub','Install from GitHub',[
        code(`python -m venv .venv
.venv\\Scripts\\python -m pip install "fncbale @ git+https://github.com/milad01rmz/fncbale.git@v0.1.36"`,'Windows · PowerShell','shell'),
        code(`python3 -m venv .venv
.venv/bin/python -m pip install "fncbale @ git+https://github.com/milad01rmz/fncbale.git@v0.1.36"`,'Linux','shell'),
        p('این روش به Git نیاز دارد. اگر Git نصب نیست، wheel نسخه را از Releases دانلود و نصب کن. فعلاً نصب سادهٔ pip install fncbale از PyPI وعده داده نمی‌شود.','This method requires Git. If Git is unavailable, download and install the wheel from Releases. A plain pip install fncbale from PyPI is not promised for this release.'),
        code(`python -m pip install ./fncbale-0.1.36-py3-none-any.whl
python -c "import fncbale; print(fncbale.__version__)"`,'Wheel & version check','shell')
      ]),
      section('checkout','استفاده از مثال‌ها','Use the examples',[
        code(`git clone https://github.com/milad01rmz/fncbale.git
cd fncbale
python -m pip install .
python examples/login.py account.session
python examples/chat_id.py account.session @yourchannel`,'Repository examples','shell'),
        note('فایل‌های محلی','Local files','session و پوشهٔ data_dir را خصوصی نگه دار و در Git ثبت نکن. برای یک حساب، تنها یک Client فعال در هر زمان داشته باش.','Keep session files and data_dir private and out of Git. Run only one active Client for the same account at a time.')
      ])
    ]},
    {id:'authentication',group:'start',icon:'key',title:t('ورود و نگهداری نشست','Login and sessions'),summary:t('ورود بومی با شماره و کد؛ ذخیرهٔ session و اتصال بعدی بدون واردکردن دوبارهٔ کد.','Native phone-and-code login, a saved session, and reconnects without requesting a new code.'),sections:[
      section('first-login','اولین ورود','First login',[
        code(`import asyncio
import getpass
from fncbale import Client

async def read_code(_challenge):
    return await asyncio.to_thread(getpass.getpass, "Login code: ")

async def read_password():
    return await asyncio.to_thread(getpass.getpass, "Account password: ")

async def main():
    phone = await asyncio.to_thread(input, "Phone number: ")
    client = Client("account.session", data_dir=".fncbale/app")
    try:
        await client.login(phone.strip(), read_code,
                           password_callback=read_password)
        await client.connect()
        print("Connected; session saved.")
    finally:
        await client.close()

asyncio.run(main())`,'login.py'),
        p('callback رمز فقط وقتی سرور واقعاً درخواست رمز دوم کند اجرا می‌شود. کد و رمز را در log ننویس. login نشست را ذخیره می‌کند؛ connect اتصال دریافت و ارسال را راه می‌اندازد.','The password callback runs only when the server requests a second factor. Never log the code or password. login saves the session; connect starts messaging and event reception.'),
        note('پوشش رمز دوم','Second-factor coverage','مسیر رمز دوم پیاده‌سازی و آفلاین آزموده شده؛ ورود با رمز دوم واقعی هنوز پذیرش زندهٔ جداگانه می‌خواهد.','Second-factor handling is implemented and tested offline; real second-factor login still needs separate live acceptance.')
      ]),
      section('reuse','اتصال‌های بعدی','Next connections',[
        code(`async with Client("account.session", data_dir=".fncbale/app") as client:
    peer = await client.resolve_peer("@yourchannel")
    print(peer.id)`,'Inside an async function'),
        p('همان session و data_dir را نگه دار. اتصال بعدی عملیات پذیرفته‌شدهٔ قبلی را هم ادامه می‌دهد. disconnect برای قطع موقت است؛ close پایان دائمی همان شیء Client است.','Keep the same session and data_dir. Reconnecting also resumes previously accepted operations. disconnect is temporary; close permanently ends that Client object.')
      ]),
      section('staged','ورود در رابط کاربری','Login in an application UI',[
        code(`from fncbale import PasswordRequired

challenge = await client.start_login(phone)
# Read the code in your UI, then complete the same challenge.
try:
    session = await client.complete_login(challenge, code)
except PasswordRequired as required:
    session = await client.complete_password_login(
        required.challenge, password
    )`,'Staged login'),
        p('challenge متعلق به همان Client است و در حافظه می‌ماند. برای اصلاح کد اشتباه، completion همان challenge را دوباره انجام بده؛ برای هر تلاش کد جدید درخواست نکن.','The challenge belongs to the same Client and stays in memory. To correct a rejected code, retry completion on that challenge rather than requesting another login code.')
      ]),
      section('import','واردکردن نشست پژوهشی','Import an existing research session',[
        code(`from fncbale import Session, SessionFile

session = Session.import_aiobale("existing.bale")
await SessionFile("account.session").save(session)`,'Explicit importer'),
        p('این importer صریح برای پاسخ auth بومیِ سازگار است؛ فرمت هر SDK دلخواه را تبدیل نمی‌کند و نیازی به نصب AioBale ندارد.','This explicit importer accepts compatible native auth-response data. It does not convert arbitrary SDK session formats and does not require AioBale.')
      ])
    ]},
    {id:'chat-id',group:'start',icon:'target',title:t('گرفتن چت‌آیدی','Find a chat ID'),summary:t('اول مقصد را resolve کن. شناسهٔ عددی به‌تنهایی نوع مقصد و دسترسی لازم را مشخص نمی‌کند.','Resolve the destination first. A numeric ID alone does not identify its kind or carry its access information.'),sections:[
      section('username','از username به Peer','From username to Peer',[
        code(`import asyncio
from fncbale import Client

async def main():
    async with Client("account.session", data_dir=".fncbale/chat-id") as client:
        peer = await client.resolve_peer("@yourchannel")
        print("chat_id:", peer.id)
        print("kind:", peer.kind.value)
        print("username:", peer.username)
        # Use the resolved Peer directly for future calls.
        group = await client.get_full_group(peer)
        print("verified group ID:", group.id)

asyncio.run(main())`,'chat_id.py'),
        p('resolve_peer نام کاربری را دقیق تطبیق می‌دهد و اطلاعات مقصد را کامل می‌کند. برای send_message همان peer را بده؛ لازم نیست ID را دوباره به عدد خام تبدیل کنی. get_full_group فقط برای گروه و کانال است.','resolve_peer matches the exact username and hydrates the destination. Pass that Peer to send_message rather than reducing it to a bare number. get_full_group is for groups and channels only.'),
        code(`python examples/chat_id.py account.session @yourchannel`,'CLI shortcut','shell')
      ]),
      section('numeric','اگر ID را از قبل دارم','If you already have an ID',[
        code(`from fncbale import PeerKind

peer = await client.resolve_peer(1234567890, kind=PeerKind.CHANNEL)
# Known kinds: USER, GROUP, CHANNEL.
print(peer.id, peer.kind.value)`,'Known destination kind'),
        note('ID مرورگر را حدس نزن','Do not guess from a browser ID','پارامتر uid در آدرس وب بله الزاماً شناسهٔ canonical پروتکل نیست. عدد نمونه را با ID تأییدشدهٔ خودت عوض کن. حساب باید به مقصد دسترسی داشته باشد.','The uid in a Bale web URL is not necessarily the canonical protocol ID. Replace the sample number with your verified ID. The account must have access to the destination.','caution'),
        p('اگر نوع یا access hash مقصد معتبر را می‌دانی، Peer نگه‌دار؛ access hash حساب‌محور است و نباید بین حساب‌ها مشترک فرض شود.','Keep the resolved Peer when you know the destination kind and valid access hash. Access information is account-scoped; do not assume it is interchangeable across accounts.')
      ]),
      section('incoming-id','از یک پیام دریافتی','From an incoming event',[
        code(`async for event in client.events():
    if event.peer is not None:
        print("chat_id:", event.peer.id)
        print("observed kind:", event.peer.kind.value)
    await event.ack()`,'Incoming destination'),
        p('نوع دیده‌شده در event از enum همان پیام می‌آید؛ ممکن است برای یک کانال به صورت group باشد. برای مقصد دارای username از resolve_peer استفاده کن تا نوع منطقی و اطلاعات کامل آن مشخص شوند.','The event kind follows its wire peer type and can appear as group for a channel. For a destination with a username, use resolve_peer to obtain the logical kind and full information.')
      ])
    ]},
    {id:'messages',group:'messaging',icon:'message',title:t('متن، reply و ویرایش','Text, replies, and edits'),summary:t('یک Peer معتبر، یک متن، و یک نتیجهٔ تایپ‌شده. برای تغییر یا حذف، مرجع همان پیام را نگه دار.','A resolved Peer, text, and a typed result. Keep the message reference for edits, replies, and deletions.'),sections:[
      section('send','ارسال متن و بولد','Send text and bold',[
        code(`peer = await client.resolve_peer("@yourchannel")
message = await client.send_message(peer, "Hello 👋")
formatted = await client.send_message(
    peer, "Plain text · *bold text* · _italic text_"
)`,'Inside a connected Client'),
        p('متن با قالب‌بندی خود بله فرستاده می‌شود: تک‌ستاره برای بولد و underscore برای italic. parse_mode مربوط به Telegram یا HTML ندارد؛ تگ <b> را به‌عنوان HTML تفسیر نمی‌کند. نمایش inline code با backtick وعده داده نمی‌شود.','Text uses Bale’s own formatting: single asterisks for bold and underscores for italic. There is no Telegram-style parse_mode or HTML parser; <b> is not interpreted as HTML. Backtick inline-code rendering is not promised.'),
        code(`message = await client.send_message(
    peer, "Order accepted", idempotency_key="order-2026-001"
)
print(message.rid, message.operation_id)
print(message.rpc_confirmed, message.history_verified, message.read)`,'Delivery information'),
        p('تأیید RPC، تطبیق تاریخچه و خوانده‌شدن سه وضعیت جدا هستند. idempotency_key برای یک کار ثابت است؛ همان کلید با محتوای متفاوت خطا می‌دهد. برای پیام تازه کلید تازه بساز.','RPC confirmation, history verification, and read status are separate. An idempotency_key identifies one intent; reusing it with different content raises an error. Use a new key for a new message.')
      ]),
      section('reply','ریپلای','Reply',[
        code(`reply = await client.send_message(peer, "A reply", reply_to=message)
# Or reply to the message's own destination:
reply = await client.reply(message, "Another reply")`,'Message or MessageRef'),
        p('MessageRef شامل peer، rid، date و seq است. فقط rid را نگه‌داشتن برای همهٔ عملیات کافی نیست. در کپی بین کانال‌ها، reply باید به مرجع پیام مقصد نگاشت شود.','MessageRef contains peer, rid, date, and seq. Keeping only the rid is not sufficient for every operation. When copying between channels, map replies to the destination message reference.')
      ]),
      section('edit-delete','ویرایش و حذف','Edit and delete',[
        code(`edited = await client.edit_message(message, "Updated text")
await client.delete_message(edited)

# Every message in a batch must belong to the same peer.
await client.delete_messages([message_a, message_b])`,'Message mutations'),
        p('ویرایش caption مدیا متد جدا دارد و فایل قبلی را حفظ می‌کند. امکان ویرایش و حذف به دسترسی حساب و قواعد سرور وابسته است؛ خطای permission باعث فالبک کور نمی‌شود.','Media captions have a separate edit method that preserves the existing file. Editing and deletion depend on account permissions and server rules; permission errors do not trigger blind fallback.'),
        code(`photo = await client.send_photo(peer, "photo.jpg", caption="Before")
updated = await client.edit_caption(photo, "After")`,'Caption edit')
      ])
    ]},
    {id:'media',group:'messaging',icon:'image',title:t('مدیا و آلبوم','Media and albums'),summary:t('عکس، ویدیو، صوت، ویس و فایل؛ آلبوم‌های ۲ تا ۱۰ آیتمی با ترتیب و metadata واقعی.','Photos, video, audio, voice, and documents. Albums of 2–10 items with preserved order and real metadata.'),sections:[
      section('single','ارسال تکی با caption','Single media with a caption',[
        code(`photo = await client.send_photo(peer, "photo.jpg", caption="A photo")
video = await client.send_video(peer, "clip.mp4", caption="A short video")
audio = await client.send_audio(peer, "track.mp3", caption="Audio")
voice = await client.send_voice(peer, "voice.ogg", caption="Voice")
document = await client.send_document(peer, "report.pdf", caption="Report")`,'Five media kinds'),
        p('برای فایل‌ها نام و MIME اختیاری است. ابعاد و مدت از فایل واقعی استخراج می‌شوند؛ تبدیل کیفیت یا فرمت خودکار انجام نمی‌شود. ورودی می‌تواند مسیر، bytes، فایل یا async stream باشد.','Filename and MIME overrides are optional. Dimensions and duration are read from the actual file; no automatic quality or format conversion takes place. Inputs can be paths, bytes, file objects, or async streams.'),
        code(`await client.send_document(
    peer, b"hello\\n", filename="hello.txt", mime_type="text/plain"
)`,'Bytes input')
      ]),
      section('album','یک آلبوم عکس و ویدیو','A photo and video album',[
        code(`from fncbale import Media, MediaKind

album = await client.send_album(peer, [
    Media("first.jpg", MediaKind.PHOTO, caption="Album caption"),
    Media("clip.mp4", MediaKind.VIDEO),
    Media("last.png", MediaKind.PHOTO),
], idempotency_key="album-2026-001")

print(album.grouped_id)
for item in album.messages:
    print(item.rid, item.media.kind)`,'Mixed album'),
        p('کل آلبوم پیش از آپلود اعتبارسنجی می‌شود. عکس و ویدیو را می‌توان ترکیب کرد؛ فایل، صوت و ویس عضو آلبوم نسخهٔ اول نیستند. ترتیب ورودی حفظ می‌شود و شکست آلبوم آن را خودکار به پیام‌های تکی تبدیل نمی‌کند.','The entire album is validated before upload. Photos and videos can be mixed; documents, audio, and voice are outside this album contract. Input order is preserved, and a failed album is not automatically split into individual messages.'),
        note('caption قابل‌نمایش در وب','A visible gallery caption','برای caption مشترک در گالری فعلی وب بله، متن را روی اولین آیتم بگذار و caption بقیه را خالی نگه دار. captionهای چند آیتم در تاریخچه حفظ می‌شوند، ولی وب ممکن است caption سطح آلبوم را نشان ندهد.','For a shared caption in the current Bale web gallery, set it on the first item and leave the rest empty. Multiple item captions remain in history, but the web gallery may hide the album-level caption.')
      ]),
      section('progress','پیشرفت و فایل پایدار','Progress and durable input',[
        code(`def progress(done, total):
    print(done, total)

await client.send_video(peer, "clip.mp4", progress=progress)`,'Upload progress'),
        p('پیش از پذیرش پایدار، یک نسخهٔ تغییرناپذیر از ورودی در spool ذخیره می‌شود. آن را تا تعیین نتیجهٔ عملیات پاک نکن. آپلود قطع‌شده با تخصیص جدید از ابتدا شروع می‌شود؛ resume اثبات‌نشده فرض نمی‌شود.','Before durable acceptance, an immutable input copy is saved in the spool. Keep it until the operation is resolved. Interrupted uploads restart with a new allocation; unverified resumability is not assumed.'),
        p('MediaInfo.duration_seconds همیشه ثانیه است. تبدیل واحد خاص ویدیو و صوت/ویس در adapter پروتکل انجام می‌شود.','MediaInfo.duration_seconds is always in seconds. The protocol adapter handles the different video and audio/voice wire units.')
      ]),
      section('download','دانلود و بررسی هش','Download and verify a hash',[
        code(`path = await client.download(
    photo, "downloads/photo.jpg",
    expected_sha256=expected_hash,
)
paths = await client.download_album(album, "downloads/album")`,'Streamed downloads'),
        p('expected_hash هش SHA256 مورد انتظار توست و اختیاری است. فایل نهایی بعد از بررسی و جایگزینی اتمیک ثبت می‌شود. دانلود گروهی می‌تواند موفقیت جزئی داشته باشد؛ BatchDownloadError.results نتیجهٔ هر فایل را نگه می‌دارد.','expected_hash is your optional expected SHA256. The final file is committed after validation and atomic replacement. A batch can partially succeed; BatchDownloadError.results records each file’s outcome.')
      ])
    ]},
    {id:'events',group:'messaging',icon:'activity',title:t('دریافت پیام و eventها','Messages and events'),summary:t('دو شیوهٔ دریافت: callback با ACK خودکار، یا iterator با تأیید صریح پس از پردازش.','Two delivery styles: callbacks with automatic ACK, or an iterator with explicit acknowledgement after processing.'),sections:[
      section('router','دریافت با Router','Receive with a Router',[
        code(`import asyncio
from fncbale import Client, Router

router = Router()

@router.on("new")
async def new_message(event):
    if event.message is not None:
        print(event.peer.id, event.message.text)

@router.on("edit")
async def edited_message(event):
    print("edited:", event.message.rid)

@router.on("delete")
async def deleted_message(event):
    print("deleted:", event.rids)

async def main():
    async with Client("account.session", router=router,
                      data_dir=".fncbale/app"):
        await asyncio.Event().wait()

asyncio.run(main())`,'receive.py'),
        p('handler موفق خودکار ACK می‌شود. خطا پس از تعداد تلاش محدود به quarantine پایدار می‌رود. handlerها از heartbeat و دریافت شبکه جدا هستند؛ کار CPU سنگین خودت را نیز بیرون event loop اجرا کن.','A successful handler is acknowledged automatically. Repeated failures move to durable quarantine after a bounded number of attempts. Handlers are separate from heartbeat and network reception; move your own heavy CPU work off the event loop too.')
      ]),
      section('manual','تأیید دستی','Explicit acknowledgement',[
        code(`async with Client("account.session", data_dir=".fncbale/app") as client:
    async for event in client.events():
        # Persist your application result with event.event_id first.
        await process_and_save(event)
        await event.ack()`,'Application-owned processing'),
        note('تحویل ممکن است تکرار شود','Delivery may repeat','پس از crash، event تأییدنشده با event_id ثابت دوباره می‌آید. side effect برنامه را با این شناسه idempotent کن. Router و iterator مصرف‌کننده‌های جایگزین‌اند؛ هم‌زمان برای رقابت روی همان inbox استفاده نکن.','After a crash, an unacknowledged event can return with the same event_id. Make application side effects idempotent with that ID. Router and iterator are alternative consumers; do not run them as competing consumers on the same inbox.')
      ]),
      section('kinds','انواع رویداد','Event kinds',[
        table([t('نوع','Kind'),t('معنی','Meaning')],[['new / sent',t('پیام جدید یا ثبت ارسال','A new message or send update')],['edit / delete',t('ویرایش و شناسه‌های حذف‌شده','An edit or deleted message IDs')],['read / read_by_me / received',t('وضعیت‌های خواندن و دریافت طبق پروتکل','Protocol read and receipt updates')],['unknown',t('رویداد ناشناخته با دادهٔ خام','An unknown event with raw data')],['gap',t('بخشی از رویدادها از سرور قابل‌بازیابی نیست','Part of the event history cannot be recovered from the server')]]),
        p('هر envelope کامل پردازش می‌شود، نه فقط اولین event. raw و دادهٔ ناشناخته حفظ می‌شوند. وجود نوع event به معنی تولید آن در تمام کانال‌ها و تمام شرایط سرور نیست.','Every envelope is processed in full, rather than taking only its first event. Raw and unknown data remain available. An event kind being supported does not mean every channel and server condition emits it.')
      ]),
      section('failed','بررسی eventهای خطادار','Inspect failed events',[
        code(`async for event in client.iter_failed_events(limit=50):
    print(event.event_id, event.kind, event.handler_failures)

await client.replay_event(event_id)`,'Quarantine and replay'),
        p('replay_event بودجهٔ پردازش را برای تلاش مجدد باز می‌کند. discard صریح با ack همان event انجام می‌شود؛ صف خطا خودکار و بی‌خبر حذف نمی‌شود.','replay_event resets processing for another attempt. Explicitly discarding a found event uses its ack; the failure queue is not silently discarded.')
      ])
    ]},
    {id:'reliability',group:'operations',icon:'shield',title:t('عملیات پایدار و فالبک','Durability and fallback'),summary:t('کمترین ابهام، بدون ارسال کور. نتیجهٔ نامطمئن با operation_id روی دیسک می‌ماند.','Reduce uncertainty without blind retransmission. An uncertain outcome stays on disk with its operation_id.'),sections:[
      section('enqueue','پذیرش با enqueue','Accept with enqueue',[
        code(`handle = await client.enqueue_message(
    peer, "Order ready", idempotency_key="order-2026-001"
)
operation_id = handle.operation_id
# Persist operation_id with your own order.
message = await handle.wait()`,'Durable handle'),
        p('enqueue پس از commit برمی‌گردد؛ منتظر پاسخ ارسال نمی‌ماند. لغو انتظار caller عملیات پذیرفته‌شده را حذف نمی‌کند. لغو کارِ واجدشرایطِ ارسال‌نشده با handle.cancel() جداست.','enqueue returns after commit without waiting for delivery. Cancelling the caller’s wait does not remove accepted work. Cancelling eligible unsent work with handle.cancel() is a separate action.'),
        p('برای مدیا، آلبوم، ویرایش و حذف نیز enqueue متناظر وجود دارد. داده و RIDها قبل از اولین ارسال پایدار می‌شوند.','Media, albums, edits, and deletions also have matching enqueue methods. Payloads and RIDs are persisted before the first send.')
      ]),
      section('fallback','چه زمانی مسیر عوض می‌شود؟','When does the route change?',[
        step([{title:t('خطای پیش از ارسال','Failure before transmission'),text:t('تا دو تلاش روی WebSocket، سپس یک HTTP؛ همان payload و شناسه‌ها حفظ می‌شوند.','Up to two WebSocket attempts, then one HTTP attempt, using the same payload and IDs.')},{title:t('ممکن است ارسال شده باشد','The write may have reached the server'),text:t('رویداد، diff و تاریخچه برای همان عملیات بررسی می‌شوند؛ ارسال تازه ساخته نمی‌شود.','Updates, diff, and history are checked for that operation; no new send is created.')},{title:t('نتیجه هنوز اثبات نشده','The result is still unproven'),text:t('وضعیت uncertain ذخیره می‌ماند. retry نوشتن مبهم فقط با dedupe اثبات‌شدهٔ همان متد مجاز است.','The operation remains uncertain. Ambiguous-write retries require proven dedupe for that exact method.')}]),
        note('سقف تلاش، نه تضمین تعداد','An attempt ceiling, not a promise','خطای auth، validation و permission با تغییر کور مسیر حل نمی‌شود. rate limit رعایت می‌شود. verified_idempotent_methods پیش‌فرض خالی است؛ بدون شواهد آن را پر نکن.','Auth, validation, and permission failures are not fixed by blindly switching routes. Rate limits are respected. verified_idempotent_methods is empty by default; do not populate it without evidence.','caution')
      ]),
      section('inspect','بررسی پس از قطع یا ری‌استارت','Inspect after a disconnect or restart',[
        code(`from fncbale import DeliveryUncertain

try:
    message = await handle.wait()
except DeliveryUncertain as exc:
    operation = await client.reconcile_operation(exc.operation_id)
    print(operation.operation_id, operation.status)

async for operation in client.iter_operations(
    statuses=["uncertain", "failed"], limit=100
):
    print(operation.operation_id, operation.status)`,'Inspect the same operation'),
        p('پس از ری‌استارت با همان session و data_dir متصل شو. wait_operation(operation_id) همان کار را دنبال می‌کند. MessageReferencesUnavailable یعنی ارسال تأیید شده ولی مرجع دقیق آیتم‌ها هنوز خوانده نشده؛ دوباره wait کن، نه send.','Reconnect with the same session and data_dir after restart. wait_operation(operation_id) follows the existing operation. MessageReferencesUnavailable means delivery is confirmed but exact item references are not available yet; wait again rather than sending again.')
      ]),
      section('limits','مرز اعتماد','Reliability boundaries',[
        p('inbox و checkpoint همهٔ routeها در یک transaction ثبت می‌شوند. GetDiff از آخرین نقطهٔ ذخیره‌شده بازیابی می‌کند. اگر سرور بخشی از فاصله را نگه نداشته باشد، GapEvent گزارش می‌شود؛ تاریخچه جای event حذف‌شده را نمی‌سازد.','The inbox and all-route checkpoints commit in one transaction. GetDiff recovers from the saved point. If the server no longer retains part of the gap, a GapEvent reports it; history cannot reconstruct an unavailable deletion event.'),
        p('رکوردهای نهایی پیش‌فرض ۷ روز نگه داشته می‌شوند. عملیات نامطمئن، ارسال‌نشده و event تأییدنشده خودکار پاک نمی‌شوند. کمبود فضای دیسک خطای صریح می‌دهد.','Final records are retained for seven days by default. Uncertain or unsent operations and unacknowledged events are not automatically purged. Running out of disk space produces an explicit error.'),
        p('تأیید ارسال به معنی خوانده‌شدن نیست. تضمین مطلق exactly-once برای side effect برنامه یا تمام شرایط شبکه داده نمی‌شود.','Delivery confirmation is not a read receipt. Absolute exactly-once guarantees are not made for application side effects or every network condition.')
      ])
    ]},
    {id:'history',group:'messaging',icon:'history',title:t('تاریخچه و جست‌وجو','History and search'),summary:t('پیام‌ها را صفحه‌به‌صفحه بخوان؛ برای رسانه و مرجع دقیق، مدل Message را نگه دار.','Read messages page by page and keep typed Message objects for media and precise references.'),sections:[
      section('history','خواندن تاریخچه','Read history',[
        code(`async for message in client.iter_history(peer, limit=100):
    print(message.rid, message.text, message.grouped_id)

async for album in client.iter_albums(peer, limit=100):
    print(album.grouped_id, len(album.messages))`,'Bounded history'),
        p('آلبوم‌های ساخته‌شده از یک پنجرهٔ محدود ممکن است ناقص باشند. group ID نشان‌دهندهٔ تعداد قطعی آیتم‌ها نیست. محدودیت پنجره و نبود پیام قدیمی را در برنامه صریح مدیریت کن.','Albums reconstructed from a bounded window can be partial. A grouped ID does not declare an authoritative item count. Handle window limits and unavailable old messages explicitly in your application.')
      ]),
      section('search','جست‌وجوی پیام','Search messages',[
        code(`async for message in client.iter_search_messages(peer, "report", limit=30):
    print(message.rid, message.text, message.media)

# Advanced: unmodified indexed results.
async for result in client.iter_search(peer, "report", limit=30):
    print(result.result.rid)`,'Typed and raw indexed search'),
        p('جست‌وجوی تایپ‌شده caption ناقصِ ایندکس را با تاریخچه کامل می‌کند. اگر snapshot در پنجرهٔ محدود پیدا نشود SearchSnapshotUnavailable می‌دهد؛ محتوای کامل ساختگی برنمی‌گرداند.','Typed search hydrates incomplete indexed captions from history. If the snapshot is absent from the bounded window, it raises SearchSnapshotUnavailable rather than inventing a full message.')
      ]),
      section('references','نگهداری مرجع پیام','Keep the message reference',[
        table([t('فیلد','Field'),t('کاربرد','Purpose')],[['peer',t('مقصد و نوع معتبر','The destination and its kind')],['rid',t('شناسهٔ پیام روی wire','The wire message ID')],['date',t('زمان لازم برای برخی درخواست‌ها','The timestamp required by some requests')],['seq',t('شمارهٔ توالی در صورت وجود','The sequence when available')]]),
        p('یک Message تایپ‌شده علاوه بر ref، text، media، grouped_id و raw دارد. raw برای بررسی حرفه‌ای پروتکل است؛ ممکن است محتوای خصوصی داشته باشد و نباید عمومی log شود.','A typed Message also has text, media, grouped_id, and raw. Raw bytes are useful for protocol work but can contain private content; do not log them publicly.')
      ])
    ]},
    {id:'copy',group:'messaging',icon:'copy',title:t('کپی و اتصال کانال‌ها','Copy and channel mirrors'),summary:t('ارسال مستقل در مقصد، با حفظ محتوا؛ نگاشت reply و eventها وظیفهٔ لایهٔ mirror است.','Independent destination sends with preserved content. Reply and event mapping belongs to the mirror layer.'),sections:[
      section('copy-message','کپی مستقل یک پیام','Copy a message independently',[
        code(`target = await client.resolve_peer("@destination")
copied = await client.copy_message(
    target, source_message, idempotency_key="copy-post-001"
)`,'Independent send'),
        p('copy_message از SendMessage استفاده می‌کند و برچسب forward نمی‌سازد. در صورت مجازبودن مرجع فایل، دانلود و آپلود دوباره لازم نیست. قالب متن، caption و metadata حفظ می‌شوند.','copy_message uses SendMessage and does not create a forward label. Reusable file references avoid downloading and uploading again when permissions permit. Formatting, captions, and metadata are preserved.'),
        p('ردشدن مرجع فایل خودکار به forward یا آپلود تبدیل نمی‌شود. snapshot مبدأ در پنجرهٔ محدود تاریخچه بررسی می‌شود؛ مقصد و مبدأ باید برای حساب قابل‌دسترسی باشند.','A rejected file reference does not automatically turn into forwarding or an upload. Source snapshots are checked in a bounded history window; both peers must be accessible to the account.')
      ]),
      section('copy-album','کپی آلبوم و reply','Copy albums and replies',[
        code(`copied_album = await client.copy_album(
    target, source_album, idempotency_key="copy-album-001"
)
reply_copy = await client.copy_message(
    target, source_reply, reply_to=copied
)`,'Album and target reply reference'),
        p('مرجع reply باید متعلق به پیام مقصد باشد. API عمومی source reply را خودکار نگاشت نمی‌کند. آلبوم کامل ۲ تا ۱۰ عکس/ویدیو لازم است؛ آلبوم ناقص نباید موفق کامل معرفی شود.','The reply reference must point to the destination message. The generic API does not automatically map source replies. Provide a complete 2–10 photo/video album; a partial album must not be presented as complete.')
      ]),
      section('mirror','اتصال مداوم دو کانال','Keep two channels connected',[
        code(`python -m examples.channel_mirror account.session --help
python -m examples.channel_chain account.session --help`,'Mirror examples','shell'),
        p('نمونهٔ channel_mirror نگاشت مبدأ به مقصد را پایدار می‌کند و new، edit و delete را روی همان پیام مقصد اعمال می‌کند. channel_chain دو mirror را در یک Client ترکیب می‌کند. مقصدها و session را پیش از اجرا با کانال‌های خودت تنظیم کن.','The channel_mirror example persists source-to-target mappings and applies new, edit, and delete to the corresponding target message. channel_chain composes two mirrors in one Client. Configure its session and destinations for your own channels before running it.'),
        note('تاریخچه با event فرق دارد','History is not an event log','نمونهٔ chain بررسی محدود تاریخچه دارد؛ نبود پیام در یک پنجره به معنی حذف نیست. حذف باید از event واقعی بیاید. آیتم دیررس آلبوم با gap صریح گزارش می‌شود، نه نادیده‌گرفتن خاموش.','The chain example supplements events with bounded history checks. Absence from a window does not prove deletion; deletion comes from a real event. A late missing album sibling produces an explicit gap rather than disappearing silently.')
      ])
    ]},
    {id:'pool',group:'operations',icon:'users',title:t('چند حساب و منابع مشترک','Multiple accounts'),summary:t('هر حساب یک Client مستقل؛ هم‌زمانی و منابع مشترک در AccountPool محدود می‌شوند.','One independent Client per account, with bounded shared resources in AccountPool.'),sections:[
      section('pool','ساخت pool','Create a pool',[
        code(`import asyncio
from fncbale import AccountPool

async def main():
    async with AccountPool(data_dir=".fncbale/pool") as pool:
        first = pool.add("first", "first.session")
        second = pool.add("second", "second.session")
        await asyncio.gather(first.connect(), second.connect())
        peers = await asyncio.gather(
            first.resolve_peer("@yourchannel"),
            second.resolve_peer("@yourchannel"),
        )
        print(peers[0].id, peers[1].id)

asyncio.run(main())`,'Independent account sessions'),
        p('sessionها باید برای دو حساب واقعاً متفاوت باشند. دو Client با همان حساب خطای SessionInUse می‌دهند. نام‌ها و مسیر pool را پس از ری‌استارت ثابت نگه دار.','Sessions must belong to distinct accounts. Two Clients for the same account raise SessionInUse. Keep pool names and its data layout stable across restarts.')
      ]),
      section('limits','حدود پیش‌فرض','Default limits',[
        table([t('منبع','Resource'),t('هر حساب','Per account'),t('کل pool','Whole pool')],[['RPC','32','256'],[t('آپلود','Upload'),'2','8'],[t('دانلود','Download'),'4','16'],[t('صف دریافت','Receive queue'),'256',t('حساب‌محور','Account-scoped')],[t('outbox','Outbox'),'4096',t('حساب‌محور','Account-scoped')]]),
        p('پرشدن صف backpressure می‌دهد، نه حذف خاموش. عملیات هر peer مرتب اجرا می‌شوند؛ peerهای مستقل موازی‌اند. metadata بیرون event loop پردازش می‌شود.','Full queues apply backpressure rather than silently dropping work. Operations for one peer stay ordered while independent peers can run concurrently. Metadata processing runs outside the event loop.'),
        code(`from fncbale import Config

config = Config(rpc_limit=16, global_rpc_limit=128,
                upload_limit=2, global_upload_limit=6)
pool = AccountPool(data_dir=".fncbale/pool", config=config)`,'Tune bounded concurrency')
      ]),
      section('measure','کارایی را اندازه بگیر','Measure performance',[
        p('مدل‌های آفلاین ۱۰۰ Client آزموده شده‌اند؛ این به معنی آزمون ۱۰۰ حساب واقعی یا تضمین سرعت شبکه نیست. سقف‌ها را با CPU، دیسک، اندازهٔ مدیا و rate limit برنامه تنظیم کن.','Offline models cover 100 Clients. This is not a test of 100 authenticated accounts or a network throughput guarantee. Tune limits against CPU, disk, media sizes, and your observed rate limits.'),
        p('SQLite با WAL و synchronous=FULL ثبت پایدار را مقدم می‌داند؛ writer خارج event loop و commit گروهی کوتاه هزینه را کنترل می‌کنند.','SQLite WAL with synchronous=FULL prioritizes durable acceptance. A writer outside the event loop and short grouped commits control the cost.')
      ])
    ]},
    {id:'members',group:'operations',icon:'eye',title:t('اعضا، تعداد و بازدید','Members and views'),summary:t('صفحه‌بندی اعضا با cursor باینری؛ خواندن بازدید بدون افزایش شمارنده.','Member pagination with opaque binary cursors and view reads that do not increment counters.'),sections:[
      section('members','صفحه‌بندی اعضا','Paginate members',[
        code(`page = await client.get_member_page(peer, page_size=50)
for member in page.members:
    print(member.uid)

# Save next_cursor only after processing the page durably.
if not page.complete:
    following = await client.get_member_page(
        peer, cursor=page.next_cursor, page_size=50
    )`,'Resumable page reads'),
        p('cursor را bytes دست‌نخورده نگه دار؛ آن را به عدد یا متن حدسی تبدیل نکن. همراه حساب، peer و تنظیمات همان اسکن ذخیره کن. تغییر عضویت می‌تواند اعتبار cursor سرور را عوض کند.','Keep the cursor as untouched bytes, without guessing an integer or text representation. Save it with the account, peer, and scan settings. Membership changes may affect server cursor validity.'),
        code(`count = await client.member_count(peer)
async for member in client.iter_members(peer, page_size=50, limit=200):
    print(member.uid)`,'Convenient bounded iterator'),
        p('iter_members در همان اجرا UIDهای تکراری را حذف می‌کند؛ برای اسکن‌های خیلی بزرگ، get_member_page کنترل حافظهٔ روشن‌تری دارد. دسترسی اعضا به مجوز حساب وابسته است.','iter_members deduplicates UIDs during that iterator run. get_member_page offers explicit memory control for large scans. Member access depends on account permissions.')
      ]),
      section('views','خواندن بازدید','Read views',[
        code(`refs = [message_a.ref, message_b.ref]
async for item in client.iter_views(peer, refs, batch_size=100):
    if item.available:
        print(item.ref.rid, item.count)
    else:
        print(item.ref.rid, "unavailable")`,'Read without incrementing'),
        p('iter_views همیشه increment=False است و ترتیب ورودی را حفظ می‌کند. count=None یعنی ناموجود؛ صفرِ موجود با آن فرق دارد. بازدید، read receipt یا snapshot دائمی نیست.','iter_views always uses increment=False and preserves input order. count=None means unavailable and differs from a known zero. Views are observations, not read receipts or a permanent snapshot.')
      ])
    ]},
    {id:'api',group:'reference',icon:'braces',title:t('مرجع API','API reference'),summary:t('مدل‌ها و متدهای پرکاربرد، کنار هم. جزئیات کامل رفتار در راهنمای Markdown مخزن است.','Common models and methods in one place. Detailed operational contracts are in the repository’s Markdown API guide.'),sections:[
      section('models','مدل‌های اصلی','Core models',[
        table([t('مدل','Model'),t('نقش','Purpose')],[['Client',t('اتصال و عملیات یک حساب','Connection and operations for one account')],['Peer(kind, id, access_hash)',t('مقصد تایپ‌شده','A typed destination')],['Message / MessageRef',t('محتوا و مرجع دقیق پیام','Message content and its precise reference')],['Media / MediaKind / MediaInfo',t('ورودی فایل، نوع و metadata','File input, kind, and metadata')],['Album',t('پیام‌های عضو و grouped_id','Ordered member messages and grouped_id')],['Event / GapEvent / UnknownEvent',t('رویداد و دادهٔ خام','Events and raw data')],['OperationHandle / Operation',t('انتظار و بررسی عملیات پایدار','Wait for and inspect durable operations')],['Router / FSM / Conversation',t('پردازش، وضعیت و گفت‌وگوی محدود','Dispatch, persisted state, and scoped conversation')],['AccountPool / Config',t('منابع چندحسابی و حدود','Multi-account resources and limits')]])
      ]),
      section('methods','متدهای روزمره','Everyday methods',[
        table([t('متد','Method'),t('خروجی یا رفتار','Result or behavior')],[['resolve_peer(value, kind=...)','Peer'],['get_full_group(peer)',t('protobuf تایپ‌شدهٔ اطلاعات گروه','Typed full-group protobuf')],['send_message(peer, text, ...)','Message'],['send_photo / send_video / send_audio / send_voice / send_document','Message'],['send_album(peer, items, ...)','Album'],['reply(message, text, ...)','Message'],['edit_message / edit_caption','Message'],['delete_message / delete_messages',t('شناسه‌های حذف‌شده','Deleted RIDs')],['copy_message / copy_album',t('ارسال مستقل Message / Album','Independent Message / Album sends')],['iter_history / iter_search_messages',t('async iterator از Message','Async Message iterator')],['download / download_album',t('مسیر فایل / مسیرها','File path / paths')],['events()',t('async iterator از Event با ack','Async Event iterator with ack')],['get_operation / reconcile_operation','Operation'],['wait_operation(operation_id)',t('نتیجهٔ همان عملیات','The same operation’s result')]]),
        p('متدهای send_* به enqueue متناظر و wait متصل‌اند. enqueue_message، enqueue_media، enqueue_album، enqueue_copy_*، enqueue_edit_* و enqueue_delete_* برای پذیرش مستقل از انتظار مناسب‌اند.','send_* methods combine durable enqueue with wait. enqueue_message, enqueue_media, enqueue_album, enqueue_copy_*, enqueue_edit_*, and enqueue_delete_* separate acceptance from waiting.')
      ]),
      section('fsm','وضعیت برنامه و middleware','Application state and middleware',[
        code(`await client.fsm.set("job:001", {"state": "received"})
state = await client.fsm.get("job:001")

@router.middleware
async def instrument(event, call_next):
    await call_next(event)`,'Account-scoped state'),
        p('FSM حساب‌محور و پایدار است. با update اتمیک وضعیت را تغییر بده. Conversation صف محدود و محدودهٔ peer دارد؛ مصرف‌کنندهٔ شبکهٔ جداگانه نیست.','FSM is account-scoped and persistent. Use atomic update for state changes. Conversation has a bounded, peer-scoped queue; it is not a second network consumer.')
      ]),
      section('raw','درخواست خام و امکانات جانبی','Raw requests and secondary helpers',[
        code(`from fncbale import contract

request = contract("GetContacts").request()
response_bytes = await client.invoke_raw(
    contract("GetContacts").service, "GetContacts",
    request.SerializeToString(), retry_policy="readonly"
)`,'Explicit read policy'),
        p('invoke_raw سیاست retry صریح می‌خواهد. برای نوشتن خام از none استفاده می‌شود؛ تشخیص نتیجه و شناسه‌های مناسب بر عهدهٔ caller است. صرف وجود descriptor، اثبات پشتیبانی زنده نیست.','invoke_raw requires an explicit retry policy. Raw writes use none; the caller owns appropriate IDs and result interpretation. A descriptor existing does not prove live support.'),
        p('get_contacts، get_dialogs، get_full_user و helperهای گروه/پروفایل نیز وجود دارند. وضعیت پذیرش هر دسته را در پشتیبانی ببین؛ قابلیت جانبی را هم‌سطح هسته فرض نکن.','Contacts, dialogs, full-user reads, and group/profile helpers are also available. Consult the support guide for their acceptance scope rather than assuming every helper has core-level coverage.')
      ])
    ]},
    {id:'troubleshooting',group:'reference',icon:'help',title:t('خطاها و رفع مشکل','Troubleshooting'),summary:t('اول نوع خطا و operation_id را ببین؛ ارسال تازه معمولاً اولین راه‌حل نیست.','Start with the error type and operation_id. Creating a new send is usually not the first fix.'),sections:[
      section('common','خطاهای رایج','Common errors',[
        table([t('خطا','Error'),t('چه کار کنم؟','What to do')],[['SessionInUse',t('Client یا process دیگر همان حساب را پیدا و هماهنگ متوقف کن. قفل را دور نزن.','Coordinate with the other Client or process using that account. Do not bypass the ownership lock.')],['PeerKindRequired',t('username را resolve کن یا نوع معتبر USER/GROUP/CHANNEL را بده.','Resolve a username or specify the verified USER/GROUP/CHANNEL kind.')],['DeliveryUncertain',t('همان operation_id را reconcile و بررسی کن؛ RID تازه نساز.','Reconcile and inspect the same operation_id. Do not create a new RID.')],['MessageReferencesUnavailable',t('ارسال تأیید شده؛ دوباره روی همان عملیات wait کن.','Delivery is confirmed; wait again on the same operation.')],['IdempotencyConflict',t('کلید قبلی برای محتوای دیگر استفاده شده؛ intent را بررسی کن.','The key was reused for a different payload; check the intent.')],['HistoryPaginationGap / GapEvent',t('محدودیت تاریخچه یا فاصلهٔ سرور را صریح در برنامه مدیریت کن.','Handle the history boundary or server recovery gap explicitly.')],['BatchDownloadError',t('results را بخوان؛ فایل‌های موفق موجودند و فقط شکست‌ها نیاز به بررسی دارند.','Inspect results. Successful files remain available; investigate failed entries.')],['AuthenticationError',t('اعتبار session و دسترسی حساب را بررسی کن؛ درخواست‌های کد را بی‌وقفه تکرار نکن.','Check the session and account access. Do not repeatedly request login codes.')]])
      ]),
      section('checklist','پیش از تغییر کد','Before changing code',[
        step([{title:t('هویت مقصد','Destination identity'),text:t('Peer معتبر است؟ UID مرورگر را با ID واقعی اشتباه نگرفتی؟','Is the Peer valid? Did you mistake a browser UID for a canonical ID?')},{title:t('نتیجهٔ پایدار','Durable result'),text:t('operation_id و وضعیت queued، confirmed یا uncertain را بررسی کن.','Inspect operation_id and queued, confirmed, or uncertain status.')},{title:t('ورودی مدیا','Media input'),text:t('فایل خوانا، فرمت واقعی و فضای spool کافی است؟ آلبوم کامل ۲ تا ۱۰ آیتم دارد؟','Is the file readable and valid, with enough spool space? Does the album have 2–10 complete items?')},{title:t('مصرف‌کننده و ACK','Consumer and ACK'),text:t('Router یا iterator فعال است؟ نتیجهٔ برنامه پیش از ACK ثبت می‌شود؟ quarantine را دیدی؟','Is a Router or iterator running? Is your result saved before ACK? Have you checked quarantine?')}]),
        p('برای گزارش مشکل، نسخه، سیستم‌عامل، متد، نوع خطا و یک مثال کوچک بدون اطلاعات خصوصی بده. session، توکن، OTP، raw پیام و URL امضاشده را در issue قرار نده.','For an issue, include the version, OS, method, error type, and a minimal example without private data. Do not attach sessions, tokens, OTPs, raw messages, or signed URLs.')
      ])
    ]},
    {id:'support',group:'reference',icon:'check',title:t('پشتیبانی و وضعیت نسخه','Support and release status'),summary:t('پوشش واقعی را از قابلیت آزمایشی جدا ببین. این نسخه alpha است و شواهد آزمون محدودهٔ مشخص دارند.','Distinguish accepted capabilities from experimental ones. This is an alpha with explicitly scoped test evidence.'),sections:[
      section('coverage','چه چیزهایی آزموده شده‌اند؟','What has acceptance coverage?',[
        table([t('دسته','Area'),t('وضعیت','Status')],[[t('متن، reply، edit و delete','Text, reply, edit, and delete'),t('هسته؛ آزمون زنده و آفلاین','Core; live and offline tests')],[t('عکس، ویدیو، صوت، ویس و فایل','Photo, video, audio, voice, and document'),t('هسته؛ metadata و هش دانلود بررسی شده','Core; metadata and downloaded hashes checked')],[t('آلبوم مخلوط ۲ و ۱۰ آیتمی','Mixed 2- and 10-item albums'),t('هسته؛ ترتیب، grouping و ACK گم‌شده آزموده شده','Core; order, grouping, and lost-ACK handling tested')],[t('new، edit، delete و بازیابی','New, edit, delete, and recovery'),t('هسته؛ قطع و ری‌استارت در کانال‌های کنترل‌شده','Core; disconnect and restart in controlled channels')],[t('کپی و mirror مستقل','Independent copy and mirrors'),t('زنده؛ نگاشت، reply و فایل‌های واقعی','Live; mappings, replies, and real files')],[t('اعضا و بازدید','Members and views'),t('خواندن زندهٔ محدود؛ مجوزها و کانال‌های بزرگ جدا','Bounded live reads; large/changing groups and permissions remain separate')],[t('forward_album','forward_album'),t('آزمایشی؛ آزمون آفلاین، بدون پذیرش زنده','Experimental; offline tests without live acceptance')],[t('ورود رمز دوم و چندحساب واقعی','Real second factor and distinct live accounts'),t('پیاده‌سازی/مدل آزموده؛ fixture واقعی تکمیلی لازم است','Implementation/model tests; additional real fixtures needed')]]),
        p('نسخهٔ فعلی ۰.۱.۳۶ است؛ CI همین نسخه از checkout تمیز روی ویندوز و لینوکس پاس شده، شامل تست‌های آفلاین، ساخت بسته، نصب و اجرای wheel و اعتبارسنجی راهنما. نتایج محلی قبلی ۰.۱.۳۵ (ویندوز ۳۸۴ پاس و یک skip؛ لینوکس ۳۸۵ پاس) سابقهٔ آزمون هستند. این اعداد پذیرش هر endpoint یا تضمین بدون خطای آینده نیستند.','The current release is 0.1.36. Its clean-checkout CI passed on Windows and Linux, including offline tests, package build, installed wheel smoke and documentation validation. Earlier local 0.1.35 results (Windows 384 passes and one skip; Linux 385 passes) are retained test history. These totals do not certify every endpoint or guarantee future error-free operation.')
      ]),
      section('sources','استقلال و منابع','Independence and sources',[
        p('تعریف‌های protobuf از BaleNova با مجوز MIT اقتباس و با قرارداد فعلی وب اصلاح شده‌اند. رفتار AioBale و Balethon برای طراحی بررسی شده؛ کد اجرایی آن‌ها داخل runtime نیست. منابع و notice در مخزن ثبت‌اند.','Protobuf definitions are adapted from MIT-licensed BaleNova and corrected against current web contracts. AioBale and Balethon behavior informed the design; their runtime implementations are not included. Provenance and notices are in the repository.'),
        p('endpoint و نسخهٔ پروتکل قابل‌تنظیم‌اند؛ سرویس بله می‌تواند تغییر کند. تغییر route فقط برای عملیات معادل و بر اساس سیاست retry انجام می‌شود.','Endpoints and protocol versions are configurable; the Bale service can change. Route switching only applies to equivalent operations under the retry policy.')
      ]),
      section('contribute','مشارکت و توسعه','Contribute',[
        code(`python -m pip install ".[dev]"
python -m pytest -q
ruff check src tests examples tools
ruff format --check src tests examples tools
python -m build --wheel`,'Offline development checks','shell'),
        p('تست‌های پیش‌فرض آفلاین‌اند و کد ورود یا پیام واقعی ایجاد نمی‌کنند. نمونه‌های ارسال و mirror فقط با session و مقصدی که خودت مجاز هستی اجرا شوند.','Default tests are offline and do not request login codes or create real posts. Run sending and mirror examples only with sessions and destinations you control.')
      ])
    ]}
  ];
  window.FNC_DOCS={version:'0.1.36',groups:[{id:'start',title:t('شروع کار','Get started')},{id:'messaging',title:t('ارسال و دریافت','Messaging')},{id:'operations',title:t('پایداری و حساب‌ها','Operations')},{id:'reference',title:t('مرجع و راهنمای خطا','Reference')}],pages};
})();
