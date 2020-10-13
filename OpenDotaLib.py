import requests
import json
import pandas as pd

OPEN_DOTA_URL = 'https://api.opendota.com/api/'

class Misc():
    def __init__(self):
        raise Exception("instance not allowed")
        
    @staticmethod
    def display(blob):
        if isinstance(blob, list) and len(blob) > 2:
            blob = [blob[0], blob[1], '...']
        print(json.dumps(blob, indent=2, ensure_ascii=False))
        return
    
    @staticmethod
    def parse(response):
        return json.loads(response.content)


class PlayerInfo():
    URL = OPEN_DOTA_URL + 'players/'
    
    def __init__(self):
        raise Exception("instance not allowed")
        
    @staticmethod
    def snapshot(player_id):
        PlayerInfo.refresh(player_id)
        shot = dict()
        shot['basic'] = PlayerInfo.basic(player_id)
        shot['id'] = shot['basic']['profile']['account_id']
        shot['name'] = shot['basic']['profile']['personaname']
        shot['win_lose'] = PlayerInfo.win_lose(player_id)
        shot['recent_matches'] = PlayerInfo.recent_matches(player_id)
        shot['all_matches'] = PlayerInfo.all_matches(player_id)
        shot['heroes'] = PlayerInfo.heroes(player_id)
        shot['peers'] = PlayerInfo.peers(player_id)
        shot['totals'] = PlayerInfo.totals(player_id)
        shot['counts'] = PlayerInfo.counts(player_id)
        shot['wardmap'] = PlayerInfo.wardmap(player_id)
        shot['ratings'] = PlayerInfo.ratings(player_id)
        shot['histograms'] = {}
        hist_list = ['actions_per_min', 'assists', 'comeback', 'courier_kills', 'deaths',
                     'denies', 'duration', 'lane_efficiency_pct', 'purchase_gem','gold_per_min', 
                     'hero_damage', 'hero_healing', 'kills', 'kda', 'last_hits', 'level', 'loss', 'pings',
                     'neutral_kills', 'purchase_ward_observer', 'purchase_rapier', 'purchase_ward_sentry',
                     'stomp', 'stuns', 'throw', 'tower_damage', 'tower_kills', 'purchase_tpscroll', 'xp_per_min']
        for field in hist_list:
            shot['histograms'][field]  = PlayerInfo.histograms(player_id, field)
        return shot
        
    @staticmethod
    def refresh(player_id):
        r = requests.post(PlayerInfo.URL + '{}/refresh'.format(player_id))
        return r
    
    @staticmethod
    def _get_blob(player_id, method=''):
        r = requests.get(PlayerInfo.URL + '{}/{}'.format(player_id, method))
        return Misc.parse(r)
    
    @staticmethod
    def basic(player_id):
        ans = PlayerInfo._get_blob(player_id, '')
        return ans
    
    @staticmethod
    def win_lose(player_id):
        ans = PlayerInfo._get_blob(player_id, 'wl')
        return ans
    
    @staticmethod
    def recent_matches(player_id):
        ans = PlayerInfo._get_blob(player_id, 'recentMatches')
        return pd.DataFrame(ans)
    
    @staticmethod
    def all_matches(player_id):
        ans = PlayerInfo._get_blob(player_id, 'matches')
        return pd.DataFrame(ans)
    
    @staticmethod
    def heroes(player_id):
        hs = PlayerInfo._get_blob(player_id, 'heroes')
        for h in hs:
            h['hero_id'] = int(h['hero_id'])
            h['name'] = HeroInfo.name(h['hero_id'])
        rs = PlayerInfo._get_blob(player_id, 'rankings')
        ans_df = pd.merge(pd.DataFrame(hs), pd.DataFrame(rs), on='hero_id', how='outer')
        return ans_df
    
    @staticmethod
    def peers(player_id):
        ans = PlayerInfo._get_blob(player_id, 'peers')
        return pd.DataFrame(ans)
    
    @staticmethod
    def totals(player_id):
        ans = PlayerInfo._get_blob(player_id, 'totals')
        return pd.DataFrame(ans)
    
    @staticmethod
    def counts(player_id):
        ans = PlayerInfo._get_blob(player_id, 'counts')
        return ans
    
    @staticmethod
    def histograms(player_id, field):
        ans = PlayerInfo._get_blob(player_id, 'histograms/' + field)
        ans_df = pd.DataFrame({
            field: [a['x'] for a in ans],
            'games': [a['games'] for a in ans],
            'wins': [a['win'] for a in ans]
        })
        return ans_df
    
    @staticmethod
    def wardmap(player_id):
        ans = PlayerInfo._get_blob(player_id, 'wardmap')
        return ans
    
    @staticmethod
    def ratings(player_id):
        ans = PlayerInfo._get_blob(player_id, 'ratings')
        return pd.DataFrame(ans)


class HeroInfo():
    _instance = None
    
    def __init__(self):
        if HeroInfo._instance != None:
            raise Exception("Singleton!")
        else:
            HeroInfo._instance = self
            r = requests.get(OPEN_DOTA_URL + 'heroes')
            heroes = Misc.parse(r)
            self.hero_dict = {}
            for hero in heroes:
                self.hero_dict[hero['id']] = hero
    
    @staticmethod
    def quantity():
        if HeroInfo._instance == None:
            HeroInfo()
        return len(HeroInfo._instance.hero_dict)

    @staticmethod
    def summary(hero_id):
        if HeroInfo._instance == None:
            HeroInfo()
        return HeroInfo._instance.hero_dict.get(hero_id, None)

    @staticmethod
    def name(hero_id):
        return HeroInfo.summary(hero_id)['localized_name']
    
    @staticmethod
    def primary(hero_id):
        return HeroInfo.summary(hero_id)['primary_attr']
    
    @staticmethod
    def roles(hero_id):
        return HeroInfo.summary(hero_id)['roles']
