import json, pprint, random, requests
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def imposta_filtri(request):
    print('imposta_filtri')
    print (request.POST)
    request.session['brand'] = request.POST.get('brand', None)
    request.session['competitor'] = request.POST.get('competitor', None)
    request.session['complexity'] = request.POST.get('complexity', '100')
    request.session['limit'] = request.POST.get('limit', '10')
    request.session['timeframe'] = request.POST.get('timeframe', request.session.get('timeframe', ''))
    request.session['start'] = request.POST.get('start', '')
    request.session['end'] = request.POST.get('end', '')

    return HttpResponse('OK')


def brand_content(request):
    return render(request, 'sito/brand.html', {'section':'brand'})

def brand_time(request):
    return render(request, 'sito/brand.html', {'section':'brand'})

def brand_hashtags(request):
    return render(request, 'sito/brand_hashtags.html', {'section':'brand'})


def community_definition(request):
    if request.method == 'POST':
        # Per il momento mettiamo gli id in sessione
        request.session['community_id'] = request.POST.getlist('community_id')
        return HttpResponseRedirect(reverse('community'))
    url = 'http://localhost:8080/communities'
    response = requests.get(url)
    elenco = []
    if (response.ok):
        data = json.loads(response.content)
        for d in data:
            d['id'] = '%d' %d['id']
            elenco.append(d)
    # TODO: gestire nomi custom
    return render(request, 'sito/community_definition.html', {'section':'community', 'elenco': elenco})

def community(request):
    community_ids = ','.join(request.session.get('community_id', []))
    url = 'http://localhost:8080/communities/graph?communities=%s&limit=10'% community_ids
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
    if tipo == 'influencers':
        url = 'http://localhost:8080/communities/graph?communities=%s&limit=%s%s%s'% (id_community, limit, start, end)
        response = requests.get(url)
        nodes = []
        if (response.ok):
            data = json.loads(response.content)
            # Trovo la dimensione massima
            max_post = 0
            for d in data['nodes']:
                if d['label'] == 'user':
                    if d['num_posts'] > max_post:
                        max_post = d['num_posts']
            for d in data['nodes']:
                if d['label'] == 'user':
                    num = 100 * d['num_posts'] / max_post
                    if num >= 75:
                        className = 'f1'
                    elif num >= 50:
                        className = 'f2'
                    elif num >= 50:
                        className = 'f3'
                    elif num >= 0:
                        className = 'f4'
                    nodes.append({
                        'title': d['username'],
                        'size': d['followers_count'],
                        'class': className
                    })
    elif tipo == 'hashtags':
        # TODO: applicare filtri temporali
        url = 'http://localhost:8080/communities/%s/%s/hashtags?limit=%s&complexity=%s%s%s' % (id_community, brand, limit, complexity, start, end)
        response = requests.get(url)
        nodes = []
        if (response.ok):
            data = json.loads(response.content)
            max_users = 0
            for k, v in data['hashtags'].items():
                if v > max_users:
                    max_users = v
            
        if competitor:
            url = 'http://localhost:8080/communities/%s/%s/hashtags?limit=%s&complexity=%s%s%s' % (id_community, competitor, limit, complexity, start, end)
            response = requests.get(url)
            nodes = []
            if (response.ok):
                data_competitor = json.loads(response.content)
                max_users = 0
                for k, v in data_competitor['hashtags'].items():
                    if v > max_users:
                        max_users = v
                
        for k, v in data['hashtags'].items():
            num = 100 * v / max_users
            if num >= 75:
                className = 'f1'
            elif num >= 50:
                className = 'f2'
            elif num >= 50:
                className = 'f3'
            elif num >= 0:
                className = 'f4'
            nodes.append({
                'title': k,
                'size': v,
                'class': className
            })

        if competitor:
            for k, v in data_competitor['hashtags'].items():
                num = 100 * v / max_users
                if num >= 75:
                    className = 'c1'
                elif num >= 50:
                    className = 'c2'
                elif num >= 50:
                    className = 'c3'
                elif num >= 0:
                    className = 'c4'
                nodes.append({
                    'title': k,
                    'size': v,
                    'class': className
                })
        random.shuffle(nodes)
    elif tipo == 'mentions':
        url = 'http://localhost:8080/communities/%s/%s/mentions?limit=%s&complexity=%s%s%s' % (id_community, brand, limit, complexity, start, end)
        response = requests.get(url)
        nodes = []
        if (response.ok):
            data = json.loads(response.content)
            max_users = 0
            for k, v in data['mentions'].items():
                if v > max_users:
                    max_users = v
        else:
            print(response.content)  
        if competitor:
            url = 'http://localhost:8080/communities/%s/%s/mentions?limit=%s&complexity=%s%s%s' % (id_community, competitor, limit, complexity, start, end)
            response = requests.get(url)
            nodes = []
            if (response.ok):
                data_competitor = json.loads(response.content)
                max_users = 0
                for k, v in data_competitor['mentions'].items():
                    if v > max_users:
                        max_users = v
        for k, v in data['mentions'].items():
                num = 100 * v / max_users
                if num >= 80:
                    className = 'f1'
                elif num >= 60:
                    className = 'f2'
                elif num >= 40:
                    className = 'f3'
                elif num >= 20:
                    className = 'f4'
                elif num >= 20:
                    className = 'f5'
                nodes.append({
                    'title': k,
                    'size': v,
                    'class': className
                })
        if competitor and data_competitor:
            for k, v in data_competitor['mentions'].items():
                num = 10 * v / max_users
                if num >= 8:
                    className = 'c1'
                elif num >= 6:
                    className = 'c2'
                elif num >= 4:
                    className = 'c3'
                elif num >= 2:
                    className = 'c4'
                else:
                    className = 'c5'
                nodes.append({
                    'title': k,
                    'size': v,
                    'class': className
                })
        random.shuffle(nodes)
    return render(request, 'sito/community-detail.html', {'section':'community', 'id_community': id_community, 'data':nodes, 'start_day': start_day,
            'end_day':end_day, 'tipo':tipo})


def change_section(request):
    if request.POST.get('switch', '') == 'community':
        return HttpResponseRedirect(reverse('community-definition'))
    return HttpResponseRedirect(reverse('brand'))
