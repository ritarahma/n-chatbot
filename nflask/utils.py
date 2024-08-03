"""Utils."""

from dateutil.relativedelta import relativedelta
import datetime
import string
import pytz
import re
import os
import json
import itertools
# from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
# from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from flask import current_app as app
# import botometer
import requests
# from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from keras import backend as K

try:
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    except ValueError:
        locale.setlocale(locale.LC_ALL, '')
except Exception as e:
    pass

TAG_HTML_REMOVE = re.compile(r'<[^>]+>')


def datettime_locale_now():
    """Datetime local indonesia."""
    # local_tz = pytz.timezone('Asia/Jakarta')
    # local_time = datetime.datetime.now(tz=local_tz)
    local_time = datetime.datetime.now()
    value = local_time
    nilai = datetime.datetime.strptime(
        value.strftime('%Y-%m-%d %H:%M:%S'),
        '%Y-%m-%d %H:%M:%S')
    return nilai


def datetime_now_to_locale(datetime_):
    """Datetime convert to local indonesia."""
    local_tz = pytz.timezone('Asia/Jakarta')
    date_time = datetime_.astimezone(local_tz)
    return date_time


def datettime_locale_server(datetime_):
    """Datetime convert to local indonesia untuk laporan atau surat."""
    # local_tz = pytz.timezone('Asia/Jakarta')
    tanggal = str(datettime_locale_now().replace(tzinfo=None).date())
    waktu = str(datettime_locale_now().time().strftime("%H:%M:%S"))
    s = '' + tanggal + ' ' + waktu + ''
    dt = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    if datetime_.replace(tzinfo=None) > datettime_locale_now():
        if datetime_.replace(tzinfo=None).time() != datettime_locale_now().time():
            dt = datettime_locale_now()
        dt = dt
    elif datetime_.replace(tzinfo=None).time() != datettime_locale_now().time():
        tanggal = str(datetime_.replace(tzinfo=None).date())
        s = '' + tanggal + ' ' + waktu + ''
        dt = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

    return dt


def get_first_month_date(year, month):
    """Ambil tanggal pertama di awal bulan."""
    first_month = datetime.date(year, month, 1)
    first_month_time = first_month.strftime("%Y-%m-%d") + " 00:00:00"
    first_month = datetime.datetime.strptime(
        first_month_time,
        '%Y-%m-%d %H:%M:%S'
    )
    return first_month


def get_last_month_date(year, month):
    """Ambil tanggal akhir di akhir bulan."""
    today = datetime.date(year, month, 1)
    d = today + relativedelta(months=1)
    last_month = datetime.date(d.year, d.month, 1) - relativedelta(days=1)
    last_month_time = last_month.strftime("%Y-%m-%d") + " 23:59:59"
    last_month = datetime.datetime.strptime(
        last_month_time,
        '%Y-%m-%d %H:%M:%S'
    )
    return last_month


def remove_tags_html(text):
    """Remove_tags_html."""
    return TAG_HTML_REMOVE.sub('', text)


def get_mimetype(filename):
    """Ambil file."""
    # Ambil extension
    filename, ext = os.path.splitext(filename)
    ext = ext.strip('.').lower()
    # Cache mimetype
    mime = 'unknown'

    # Deteksi jenis berdasarkan extension
    if ext in [
        'jpeg', 'jpg', 'png',
        'gif', 'tiff', 'bpm',
        'ico'
    ]:
        mime = 'image'
    elif ext in [
        'doc', 'docx', 'xls',
        'xlsx', 'ppt', 'pptx',
        'odf', 'odt', 'txt',
        'csv'
    ]:
        mime = 'document'
    elif ext in [
        'mp4', 'mkv', 'avi',
        '3gp', 'wmv', 'dat'
    ]:
        mime = 'video'
    elif ext in [
        'mp3', 'flac', 'wav',
        'ogg', 'm4a'
    ]:
        mime = 'audio'
    elif ext == 'pdf':
        mime = 'pdf'

    return mime


def pw_has_lowercase(pw):
    """Password must contain a lowercase letter."""
    return len(set(string.ascii_lowercase).intersection(pw)) > 0


def pw_has_uppercase(pw):
    """Password must contain an uppercase letter."""
    return len(set(string.ascii_uppercase).intersection(pw)) > 0


def pw_has_numeric(pw):
    """Password must contain a digit."""
    return len(set(string.digits).intersection(pw)) > 0


def pw_has_special(pw):
    """Password must contain a special character."""
    return len(set(string.punctuation).intersection(pw)) > 0


def remove_special(text):
    return re.sub('[^\w\. s-]','',text)

def replace_slash(text):
    return text.replace('/','-')

class node():
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


def sort_dict(dict_entity,size,nested=False, field='count'):
    if not nested:
      d = {k: v for k, v in sorted(dict_entity.items(), key=lambda item: item[1],reverse=True)}
    else:
      d = {k: v for k, v in sorted(dict_entity.items(), key=lambda x: x[1][field],reverse=True)}
    return dict(itertools.islice(d.items(), size))

def insert_sna(dict_sna,lis):
    if lis == None or type(lis)==type(""):
        lis = []
    lis = list(set(lis))
    for subset in itertools.combinations(lis,2):
        l_subset = list(subset)
        l_subset.sort()
        sna_key = '---'.join(l_subset)
        if sna_key not in dict_sna:
            dict_sna[sna_key] = [l_subset,1]
        else:
            dict_sna[sna_key][1]+=1
    return dict_sna
    
def insert_new_sna(dict_sna,nodes,lis,filters=''):
    if lis == None or type(lis)==type(""):
        lis = []
    lis = list(set(lis))
    for subset in itertools.combinations(lis,2):
        l_subset = list(subset)
        if filters.lower() not in ' '.join(l_subset).lower():
            continue
        l_subset.sort()
        sna_key = '---'.join(l_subset)
        if sna_key not in dict_sna['links']:
            dict_sna['links'][sna_key] = {"source":l_subset[0],"target":l_subset[1],"weight":1}
            nodes.extend(l_subset)
            
        else:
            dict_sna['links'][sna_key]['weight'] += 1
        
        dict_sna['filter'] = filters
            
    return dict_sna, nodes



#TF IDF
stopwords = ['https','ga','sih','yg','sakit','berharap','penyebaran','calon','kawasan','melaporkan','menurutnya','mencari','berbeda','meningkatkan','tinggal','berusia','pria','percepatan','dugaan','pt','pencegahan','juru','enam','lapangan','tingkat','lingkaran','tertulis','menilai','ruang','nya','aman','sumber','mendukung','mencegah','dilaporkan','tanggal','ribu','kepala','tim','positif','mengalami','timur','barat','selatan','utara','khusus','upaya','utama','ditemukan','tangan','menerima','bidang','menjaga','tes','dihubungi','ketiga','diduga','jarak','kemarin','barang','mudah','kebijakan','diterima','membawa','posisi','langkah','milik','penyebaram','satunya','berjalan','mengikuti','menemukan','menerapkan','bicara','dilansir','kejadian','berhasil','bantuan','pagi','akun','jam','kawasam','angka','musim','digelar','orang','salah','rumah','kesehatan','memiliki','terkait','hasil','kota','dunia','kali','langsung','jalan','menyebut','masuk','keterangan','berdasarkan','wib','tugas','informasi','proses','sesuai','sosial','kerja','mengaku','kondisi','rp','penanganan','meninggal','pemeriksaan','akibat','pusat','nomor','persen','korban','lokasi','keluarga','total','malam','ya','nama','dinyatakan','pelaku','resmi','juta','dikutip','kegiatan','pekan','mencapai','kantor','cepat','membantu','menjalani','anggota','senin','selasa','rabu','kamis','jumat','sabtu','minggu','januari','februari','maret','april','mei','juni','juli','agustus','september','november','desember','ada', 'adalah', 'adanya', 'adapun', 'agak', 'agaknya', 'agar', 'akan', 'akankah', 'akhir', 'akhiri', 'akhirnya', 'aku', 'akulah', 'amat', 'amatlah', 'anda', 'andalah', 'antar', 'antara', 'antaranya', 'apa', 'apaan', 'apabila', 'apakah', 'apalagi', 'apatah', 'artinya', 'asal', 'asalkan', 'atas', 'atau', 'ataukah', 'ataupun', 'awal', 'awalnya', 'bagai', 'bagaikan', 'bagaimana', 'bagaimanakah', 'bagaimanapun', 'bagi', 'bagian', 'bahkan', 'bahwa', 'bahwasanya', 'baik', 'bakal', 'bakalan', 'balik', 'banyak', 'bapak', 'baru', 'bawah', 'beberapa', 'begini', 'beginian', 'beginikah', 'beginilah', 'begitu', 'begitukah', 'begitulah', 'begitupun', 'bekerja', 'belakang', 'belakangan', 'belum', 'belumlah', 'benar', 'benarkah', 'benarlah', 'berada', 'berakhir', 'berakhirlah', 'berakhirnya', 'berapa', 'berapakah', 'berapalah', 'berapapun', 'berarti', 'berawal', 'berbagai', 'berdatangan', 'beri', 'berikan', 'berikut', 'berikutnya', 'berjumlah', 'berkali-kali', 'berkata', 'berkehendak', 'berkeinginan', 'berkenaan', 'berlainan', 'berlalu', 'berlangsung', 'berlebihan', 'bermacam', 'bermacam-macam', 'bermaksud', 'bermula', 'bersama', 'bersama-sama', 'bersiap', 'bersiap-siap', 'bertanya', 'bertanya-tanya', 'berturut', 'berturut-turut', 'bertutur', 'berujar', 'berupa', 'besar', 'betul', 'betulkah', 'biasa', 'biasanya', 'bila', 'bilakah', 'bisa', 'bisakah', 'boleh', 'bolehkah', 'bolehlah', 'buat', 'bukan', 'bukankah', 'bukanlah', 'bukannya', 'bulan', 'bung', 'cara', 'caranya', 'cukup', 'cukupkah', 'cukuplah', 'cuma', 'dahulu', 'dalam', 'dan', 'dapat', 'dari', 'daripada', 'datang', 'dekat', 'demi', 'demikian', 'demikianlah', 'dengan', 'depan', 'di', 'dia', 'diakhiri', 'diakhirinya', 'dialah', 'diantara', 'diantaranya', 'diberi', 'diberikan', 'diberikannya', 'dibuat', 'dibuatnya', 'didapat', 'didatangkan', 'digunakan', 'diibaratkan', 'diibaratkannya', 'diingat', 'diingatkan', 'diinginkan', 'dijawab', 'dijelaskan', 'dijelaskannya', 'dikarenakan', 'dikatakan', 'dikatakannya', 'dikerjakan', 'diketahui', 'diketahuinya', 'dikira', 'dilakukan', 'dilalui', 'dilihat', 'dimaksud', 'dimaksudkan', 'dimaksudkannya', 'dimaksudnya', 'diminta', 'dimintai', 'dimisalkan', 'dimulai', 'dimulailah', 'dimulainya', 'dimungkinkan', 'dini', 'dipastikan', 'diperbuat', 'diperbuatnya', 'dipergunakan', 'diperkirakan', 'diperlihatkan', 'diperlukan', 'diperlukannya', 'dipersoalkan', 'dipertanyakan', 'dipunyai', 'diri', 'dirinya', 'disampaikan', 'disebut', 'disebutkan', 'disebutkannya', 'disini', 'disinilah', 'ditambahkan', 'ditandaskan', 'ditanya', 'ditanyai', 'ditanyakan', 'ditegaskan', 'ditujukan', 'ditunjuk', 'ditunjuki', 'ditunjukkan', 'ditunjukkannya', 'ditunjuknya', 'dituturkan', 'dituturkannya', 'diucapkan', 'diucapkannya', 'diungkapkan', 'dong', 'dua', 'dulu', 'empat', 'enggak', 'enggaknya', 'entah', 'entahlah', 'guna', 'gunakan', 'hal', 'hampir', 'hanya', 'hanyalah', 'hari', 'harus', 'haruslah', 'harusnya', 'hendak', 'hendaklah', 'hendaknya', 'hingga', 'ia', 'ialah', 'ibarat', 'ibaratkan', 'ibaratnya', 'ibu', 'ikut', 'ingat', 'ingat-ingat', 'ingin', 'inginkah', 'inginkan', 'ini', 'inikah', 'inilah', 'itu', 'itukah', 'itulah', 'jadi', 'jadilah', 'jadinya', 'jangan', 'jangankan', 'janganlah', 'jauh', 'jawab', 'jawaban', 'jawabnya', 'jelas', 'jelaskan', 'jelaslah', 'jelasnya', 'jika', 'jikalau', 'juga', 'jumlah', 'jumlahnya', 'justru', 'kala', 'kalau', 'kalaulah', 'kalaupun', 'kalian', 'kami', 'kamilah', 'kamu', 'kamulah', 'kan', 'kapan', 'kapankah', 'kapanpun', 'karena', 'karenanya', 'kasus', 'kata', 'katakan', 'katakanlah', 'katanya', 'ke', 'keadaan', 'kebetulan', 'kecil', 'kedua', 'keduanya', 'keinginan', 'kelamaan', 'kelihatan', 'kelihatannya', 'kelima', 'keluar', 'kembali', 'kemudian', 'kemungkinan', 'kemungkinannya', 'kenapa', 'kepada', 'kepadanya', 'kesampaian', 'keseluruhan', 'keseluruhannya', 'keterlaluan', 'ketika', 'khususnya', 'kini', 'kinilah', 'kira', 'kira-kira', 'kiranya', 'kita', 'kitalah', 'kok', 'kurang', 'lagi', 'lagian', 'lah', 'lain', 'lainnya', 'lalu', 'lama', 'lamanya', 'lanjut', 'lanjutnya', 'lebih', 'lewat', 'lima', 'luar', 'macam', 'maka', 'makanya', 'makin', 'malah', 'malahan', 'mampu', 'mampukah', 'mana', 'manakala', 'manalagi', 'masa', 'masalah', 'masalahnya', 'masih', 'masihkah', 'masing', 'masing-masing', 'mau', 'maupun', 'melainkan', 'melakukan', 'melalui', 'melihat', 'melihatnya', 'memang', 'memastikan', 'memberi', 'memberikan', 'membuat', 'memerlukan', 'memihak', 'meminta', 'memintakan', 'memisalkan', 'memperbuat', 'mempergunakan', 'memperkirakan', 'memperlihatkan', 'mempersiapkan', 'mempersoalkan', 'mempertanyakan', 'mempunyai', 'memulai', 'memungkinkan', 'menaiki', 'menambahkan', 'menandaskan', 'menanti', 'menanti-nanti', 'menantikan', 'menanya', 'menanyai', 'menanyakan', 'mendapat', 'mendapatkan', 'mendatang', 'mendatangi', 'mendatangkan', 'menegaskan', 'mengakhiri', 'mengapa', 'mengatakan', 'mengatakannya', 'mengenai', 'mengerjakan', 'mengetahui', 'menggunakan', 'menghendaki', 'mengibaratkan', 'mengibaratkannya', 'mengingat', 'mengingatkan', 'menginginkan', 'mengira', 'mengucapkan', 'mengucapkannya', 'mengungkapkan', 'menjadi', 'menjawab', 'menjelaskan', 'menuju', 'menunjuk', 'menunjuki', 'menunjukkan', 'menunjuknya', 'menurut', 'menuturkan', 'menyampaikan', 'menyangkut', 'menyatakan', 'menyebutkan', 'menyeluruh', 'menyiapkan', 'merasa', 'mereka', 'merekalah', 'merupakan', 'meski', 'meskipun', 'meyakini', 'meyakinkan', 'minta', 'mirip', 'misal', 'misalkan', 'misalnya', 'mula', 'mulai', 'mulailah', 'mulanya', 'mungkin', 'mungkinkah', 'nah', 'naik', 'namun', 'nanti', 'nantinya', 'nyaris', 'nyatanya', 'oleh', 'olehnya', 'pada', 'padahal', 'padanya', 'pak', 'paling', 'panjang', 'pantas', 'para', 'pasti', 'pastilah', 'penting', 'pentingnya', 'per', 'percuma', 'perlu', 'perlukah', 'perlunya', 'pernah', 'persoalan', 'pertama', 'pertama-tama', 'pertanyaan', 'pertanyakan', 'pihak', 'pihaknya', 'pukul', 'pula', 'pun', 'punya', 'rasa', 'rasanya', 'rata', 'rupanya', 'saat', 'saatnya', 'saja', 'sajalah', 'saling', 'sama', 'sama-sama', 'sambil', 'sampai', 'sampai-sampai', 'sampaikan', 'sana', 'sangat', 'sangatlah', 'satu', 'saya', 'sayalah', 'se', 'sebab', 'sebabnya', 'sebagai', 'sebagaimana', 'sebagainya', 'sebagian', 'sebaik', 'sebaik-baiknya', 'sebaiknya', 'sebaliknya', 'sebanyak', 'sebegini', 'sebegitu', 'sebelum', 'sebelumnya', 'sebenarnya', 'seberapa', 'sebesar', 'sebetulnya', 'sebisanya', 'sebuah', 'sebut', 'sebutlah', 'sebutnya', 'secara', 'secukupnya', 'sedang', 'sedangkan', 'sedemikian', 'sedikit', 'sedikitnya', 'seenaknya', 'segala', 'segalanya', 'segera', 'seharusnya', 'sehingga', 'seingat', 'sejak', 'sejauh', 'sejenak', 'sejumlah', 'sekadar', 'sekadarnya', 'sekali', 'sekali-kali', 'sekalian', 'sekaligus', 'sekalipun', 'sekarang', 'sekarang', 'sekecil', 'seketika', 'sekiranya', 'sekitar', 'sekitarnya', 'sekurang-kurangnya', 'sekurangnya', 'sela', 'selain', 'selaku', 'selalu', 'selama', 'selama-lamanya', 'selamanya', 'selanjutnya', 'seluruh', 'seluruhnya', 'semacam', 'semakin', 'semampu', 'semampunya', 'semasa', 'semasih', 'semata', 'semata-mata', 'semaunya', 'sementara', 'semisal', 'semisalnya', 'sempat', 'semua', 'semuanya', 'semula', 'sendiri', 'sendirian', 'sendirinya', 'seolah', 'seolah-olah', 'seorang', 'sepanjang', 'sepantasnya', 'sepantasnyalah', 'seperlunya', 'seperti', 'sepertinya', 'sepihak', 'sering', 'seringnya', 'serta', 'serupa', 'sesaat', 'sesama', 'sesampai', 'sesegera', 'sesekali', 'seseorang', 'sesuatu', 'sesuatunya', 'sesudah', 'sesudahnya', 'setelah', 'setempat', 'setengah', 'seterusnya', 'setiap', 'setiba', 'setibanya', 'setidak-tidaknya', 'setidaknya', 'setinggi', 'seusai', 'sewaktu', 'siap', 'siapa', 'siapakah', 'siapapun', 'sini', 'sinilah', 'soal', 'soalnya', 'suatu', 'sudah', 'sudahkah', 'sudahlah', 'supaya', 'tadi', 'tadinya', 'tahu', 'tahun', 'tak', 'tambah', 'tambahnya', 'tampak', 'tampaknya', 'tandas', 'tandasnya', 'tanpa', 'tanya', 'tanyakan', 'tanyanya', 'tapi', 'tegas', 'tegasnya', 'telah', 'tempat', 'tengah', 'tentang', 'tentu', 'tentulah', 'tentunya', 'tepat', 'terakhir', 'terasa', 'terbanyak', 'terdahulu', 'terdapat', 'terdiri', 'terhadap', 'terhadapnya', 'teringat', 'teringat-ingat', 'terjadi', 'terjadilah', 'terjadinya', 'terkira', 'terlalu', 'terlebih', 'terlihat', 'termasuk', 'ternyata', 'tersampaikan', 'tersebut', 'tersebutlah', 'tertentu', 'tertuju', 'terus', 'terutama', 'tetap', 'tetapi', 'tiap', 'tiba', 'tiba-tiba', 'tidak', 'tidakkah', 'tidaklah', 'tiga', 'tinggi', 'toh', 'tunjuk', 'turut', 'tutur', 'tuturnya', 'ucap', 'ucapnya', 'ujar', 'ujarnya', 'umum', 'umumnya', 'ungkap', 'ungkapnya', 'untuk', 'usah', 'usai', 'waduh', 'wah', 'wahai', 'waktu', 'waktunya', 'walau', 'walaupun', 'wong', 'yaitu', 'yakin', 'yakni', 'yang']
""" find word frequencies"""
def word_frequency(texts):
#     texts=["dog cat fish","doG cat cat","fish bird", 'bird']
  cv = CountVectorizer()
  cv_fit=cv.fit_transform(texts)

  nfreq = {}
  for name,frequency in zip(cv.get_feature_names(),cv_fit.toarray().sum(axis=0)):
      nfreq[name] = frequency
  return nfreq
def find_meta_content(source, list_field):
    result = []
    for field in list_field:
        foo = source.get(field,[])
        if type(foo) == type(""):
            foo = [foo]
        foo = ' '.join([x.replace(' ','_').replace('-','_').lower() for x in foo])
        result.append(foo)
    
    return ' '.join(result)

""" find top words """
def top_words(hits,text_field,list_field):
    list_contentRaw=[]
    pattern = re.compile(r'\b(' + r'|'.join(stopwords) + r')\b\s*')
    for hit in hits:
      source = hit['_source']
      
      content = source.get(text_field,[])
      if type(content) == type([]):
        content = [x.replace(' ','_').replace('-','_').lower() for x in content]
        content = " ".join(content)
      content = content.lower()
      content = pattern.sub('', content)

      # menambahkan entity
      meta_content = find_meta_content(source,list_field)
      

      list_contentRaw.append(' ' .join([content,meta_content]))

    new_word_dict = tf_idf(list_contentRaw)
    return new_word_dict
    
""" doing ml thingy """
def tf_idf(list_contentRaw):
    vectorize = TfidfVectorizer()
    if list_contentRaw==[]:
      list_contentRaw=["no_data"]
    response= vectorize.fit_transform(list_contentRaw)
    sums = response.sum(axis=0)

    terms = vectorize.get_feature_names()
    data = {}
    for col, term in enumerate(terms):
        data[term] = sums[0,col]

    word_dict = sort_dict(data,100,nested=False)
    #find word frequencies
    nfreq = word_frequency(list_contentRaw)
    new_word_dict = [{"keyword":x, "score":word_dict[x], "count":int(nfreq.get(x,0))} for x in word_dict]

    return new_word_dict


def zero_division_handler(a:float,b:float):
    if b == 0:
        return 0
    return a/b

#utils RSA chatbot
def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

def lemma_clean(word):
    if type(word) == tuple:
        result = word[0]
    else:
        result = word

    return result
