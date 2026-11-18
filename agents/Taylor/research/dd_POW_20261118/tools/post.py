import re,sys,html
for p in sys.argv[1:]:
    s=open(p,encoding='utf-8',errors='ignore').read()
    b=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
    m=re.search(r'class="[^"]*(detail|content|entry)[^"]*"(.*)',b,re.S)
    b=html.unescape(re.sub(r'<[^>]+>','\n',b)); b=re.sub(r'\n\s*\n+','\n',b)
    print('=====',p); print(b)
