import json, pprint, random, requests
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings 

from .models import *

@csrf_exempt
def imposta_filtri(request):
    request.session['brand'] = request.POST.get('brand', None)
    request.session['competitor'] = request.POST.get('competitor', None)
    request.session['complexity'] = request.POST.get('complexity', '100')
    request.session['limit'] = request.POST.get('limit', '10')
    request.session['timeframe'] = request.POST.get('timeframe', request.session.get('timeframe', ''))
    request.session['start'] = request.POST.get('start', '')
    request.session['end'] = request.POST.get('end', '')

    return HttpResponse('OK')


def brand_content(request):
    return render(request, 'sito/brand.html', {'section':'brand',
                   'tipo': 'content', 'backend': settings.BACKEND_HOST})

def brand_time(request):
    return render(request, 'sito/brand.html', {'section':'brand',
                   'tipo': 'time', 'backend': settings.BACKEND_HOST})

def brand_hashtags_json(request, id_community = "2252447111", filter_from=None, filter_to=None):
    url = '%s/metrics/%s?window=month'%(settings.BACKEND_HOST, id_community)
    response = requests.get(url)
    if (response.ok):
        data = response.content
        return HttpResponse(data, content_type='text/json')

    raise Exception("502 - Gateway error")
    

def brand_hashtags(request):
    brand = request.session.get('brand', '2252447111')
    competitor = request.session.get('competitor', brand)
    limit = request.session.get('limit', '10')
    complexity = request.session.get('complexity', '100')
    start = request.session.get('start', '')
    end = request.session.get('end', '')

    
    return render(request, 'sito/brand_hashtags.html',
                  {'section':'brand',
                   'backend': settings.BACKEND_HOST,
                   'brand': competitor,
                   'start': start,
                   'end': end,
                   'tipo': 'hashtags'
                  })


def community_definition(request):
    if request.method == 'POST':
        # Per il momento mettiamo gli id in sessione
        lista = request.POST.getlist('community_id')
        request.session['community_id'] = lista
        for c in lista:
            new, _ = Community.objects.get_or_create(id_backend=c)
            nome = request.POST.get('name_%s'%c, None)
            if nome:
                new.name = nome
                new.save()
        return HttpResponseRedirect(reverse('community'))
    url = '%s/communities'%settings.BACKEND_HOST
    response = requests.get(url)
    elenco = []
    if (response.ok):
        data = json.loads(response.content)
        for d in data:
            d['id'] = '%d' %d['id']
            try:
                data = Community.objects.get(id_backend=d['id'])
                d['name'] = data.name
            except Community.DoesNotExist:
                pass
            elenco.append(d)
    return render(request, 'sito/community_definition.html', {'section':'community', 'elenco': elenco})

def community(request):
    community_ids = ','.join(request.session.get('community_id', []))
    url = '%s/communities/graph?communities=%s&limit=10'%(settings.BACKEND_HOST,community_ids)
    response = requests.get(url)
    edges = []
    nodes = []
    if (response.ok):
        data = json.loads(response.content)
        for d in data['edges']:
            edges.append(d)

        # Trovo il numero massimo di post per poter dimensionare i nodi
        maxPosts = 0 
        for d in data['nodes']:
            p = d.get('num_posts', 1)
            if p > maxPosts:
                maxPosts = p

        for d in data['nodes']:
            if d['id'][0] == 'u':
                d['color'] = '#c6efef'
                d['size'] = 20
            else:
                d['color'] = "#C7BBD5" 
                d['size'] = (d.get('num_posts', maxPosts) / maxPosts) * 100
            nodes.append(d)
        random.shuffle(nodes)
    return render(request, 'sito/community.html', {'section':'community', 'edges': edges, 'nodes':nodes})


def community_detail(request, id_community, tipo='influencers'):
    def color_dot(num, pref):
        if num >= 75:
            l = 1
        elif num >= 50:
            l = 2
        elif num >= 50:
            l = 3
        elif num >= 0:
            l = 4
        return "%s%d"%(pref,l)

    def color_dot_5(num, pref):
        if num >= 80:
            l = 1
        elif num >= 60:
            l = 2
        elif num >= 40:
            l = 3
        elif num >= 20:
            l = 4
        else:
            l = 5
        return "%s%d"%(pref,l)


    brand = request.session.get('brand', '2252447111')
    competitor = request.session.get('competitor', None)
    limit = request.session.get('limit', '10')
    complexity = request.session.get('complexity', '100')
    start = request.session.get('start', '')
    end = request.session.get('end', '')
    if start:
        start = '&start=%s' % start
    if end:
        end = '&end=%s' % end
    data = None
    data_competitor = None
    timeframe = request.session.get('timeframe', '')
    start_day = ''
    end_day = ''
    if timeframe:
        a = timeframe.split(' - ')
        start_day = a[0]
        end_day = a[1]

        
        
    def fn_influencers():
        
        def get_info(url):
            response = requests.get(url)
            if not response.ok:
                return {}

            data = json.loads(response.content)
            nodes_raw = [ d for d in data["nodes"] if d["label"] == "user" ]
            if len(nodes_raw) == 0:
                return {}
            max_post = max([ d["num_posts"] for d in nodes_raw])
            nodes = { d["id"]: {
                'id': d["id"],
                'title': d["username"],
                'size': d["followers_count"],
                'num_posts': d["num_posts"],
                'class': color_dot(100*d["num_posts"]/max_post, "f"),
                'border': 1
            } for d in nodes_raw }

            return nodes

        def thick_border(x):
            x["border"]=3
            x["class"] = x["class"].replace("f","c")
            return x

        url_me = '%s/communities/graph?communities=%s&limit=%s%s%s'% (settings.BACKEND_HOST, id_community, limit, start, end)
        me = get_info(url_me)
        if competitor:
            url_other = '%s/communities/graph?communities=%s&limit=%s%s%s'% (settings.BACKEND_HOST, competitor, limit, start, end)
            other = get_info(url_other)
        else:
            other = {}

        id_me = set(me.keys())
        id_other = set(other.keys())

        only_me = id_me - id_other
        common_id = id_me.intersection(id_other)

        influx_me = [ me[k] for k in only_me ]
        influx_common = [ thick_border(me[k]) for k in common_id ]

        return (False, influx_me+influx_common)

    def fn_hashtags():
        def get_info(url):
            response = requests.get(url)
            if not response.ok:
                return {}

            data = json.loads(response.content)
            if len(data["hashtags"]) == 0:
                max_users = 1
            max_users = max(list(data["hashtags"].values()))
            return { k:{ 'title':k, 'size':v, 'class':color_dot(100*v/max_users,"f"), 'max': max_users } for k,v in data["hashtags"].items() }

        def add_scale(me, other):
            me["other_size"] = other["size"]
            me["other_max"] = other["max"]

            me["scale"] = float(me["other_size"]) / (me["size"] + me["other_size"])
            return me

        url_me = '%s/communities/%s/%s/hashtags?limit=%s&complexity=%s%s%s' % (settings.BACKEND_HOST, id_community, brand, limit, complexity, start, end)
        me = get_info(url_me)
        if competitor:
            url_other = '%s/communities/%s/%s/hashtags?limit=%s&complexity=%s%s%s' % (settings.BACKEND_HOST, id_community, competitor, limit, complexity, start, end)
            other = get_info(url_other)

            id_me = set(me.keys())
            id_other = set(other.keys())

            common_id = id_me.intersection(id_other)

            return (True, [ add_scale(me[k], other[k]) for k in common_id ])

        return (False, list(me.values()))

    def fn_mentions():
        def get_info(url):
            response = requests.get(url)
            if not response.ok:
                return {}

            data = json.loads(response.content)
            if len(data["mentions"]) == 0:
                max_users = 1
            max_users = max(list(data["mentions"].values()))
            return { k:{ 'title':k, 'size':v, 'class':color_dot_5(100*v/max_users,"f"), 'max': max_users } for k,v in data["mentions"].items() }

        def add_scale(me, other):
            me["other_size"] = other["size"]
            me["other_max"] = other["max"]

            me["scale"] = float(me["other_size"]) / (me["size"] + me["other_size"])
            return me

        url_me = '%s/communities/%s/%s/mentions?limit=%s&complexity=%s%s%s' % (settings.BACKEND_HOST, id_community, brand, limit, complexity, start, end)
        me = get_info(url_me)
        if competitor:
            url_other = '%s/communities/%s/%s/mentions?limit=%s&complexity=%s%s%s' % (settings.BACKEND_HOST, id_community, competitor, limit, complexity, start, end)
            other = get_info(url_other)

            id_me = set(me.keys())
            id_other = set(other.keys())

            common_id = id_me.intersection(id_other)

            return (True, [ add_scale(me[k], other[k]) for k in common_id ])

        return (False, list(me.values()))
        
        
    if tipo == 'influencers':
        compare, nodes = fn_influencers()
    elif tipo == 'hashtags':
        compare, nodes = fn_hashtags()
    elif tipo == 'mentions':
        compare, nodes = fn_mentions()
    else:
        # error?
        compare, nodes = False, []

    if competitor:
        competitor_name = {
            "175547541" : "miguelinagambaccini",
            "8442900" : "athenaprocopiou",
            "20718070" : "lisamariefernandez",
            "332000242" : "heidikleinswim",
            "439290000" : "loupcharmant",
            "1041017111" : "zeusndione",
            "2091887150" : "daftcollectionofficial",
            "199457675" : "muzungusisters",
            "52899088" : "dodobaror",
        }.get(competitor, "competitor")
    else:
        competitor_name = ""
        
    random.shuffle(nodes)

    try:
        community = Community.objects.get(id_backend=id_community)
        community_name = community.name
    except Community.DoesNotExist:
        community_name = None
    return render(request, 'sito/community-detail.html', {'section':'community',
        'community_name': community_name,
                                                          'id_community': id_community,
                                                          'data':nodes,
                                                          'start_day': start_day,
                                                          'end_day':end_day,
                                                          'tipo':tipo,
                                                          'compare':compare,
                                                          'competitor':competitor_name,
                                                          'backend': settings.BACKEND_HOST})


def change_section(request):
    if request.POST.get('switch', '') == 'community':
        return HttpResponseRedirect(reverse('community-definition'))
    return HttpResponseRedirect(reverse('brand'))
