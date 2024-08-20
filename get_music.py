from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from lxml import etree
#使用此类必须知晓歌手id
class GetMusic:
    def __init__(self):
        self.etree = etree

    def get_page_text(self,id:str):
        # 解析网页
        target=f'https://music.163.com/artist?id={id}'
        edge_opts = Options()
        edge_opts.add_argument('--headless')
        edge_opts.add_argument('--disable-gpu')
        driver=webdriver.Edge(options=edge_opts)
        driver.get(target)
        driver.switch_to.frame(driver.find_element(By.ID, 'g_iframe'))
        page_text = driver.execute_script('return document.documentElement.outerHTML')
        driver.quit()
        return page_text
    #获取音乐名和id
    def get_music(self,id:str):
        music = etree.HTML(self.get_page_text(id))
        # res=music.xpath('/html/body/div[3]/div[1]/div/div/div[3]/div[2]/div/div/div/div[1]/table/tbody/tr[1]/td[2]/div/div/div/span/a/b')#获取音乐名list
        music_list=music.xpath('/html/body/div[3]/div[1]/div/div/div[3]/div[2]/div/div/div/div[1]/table/tbody')
        music_num=len(music_list[0].xpath('.//td'))#td的个数,即音乐标签的个数
        # res_id=music.xpath('/html/body/div[3]/div[1]/div/div/div[3]/div[2]/div/div/div/div[1]/table/tbody/tr[3]/td[2]/div/div/div/span/a')
        music_name = []
        music_id=[]
        for j in range(1,music_num):
            res = music.xpath(f'/html/body/div[3]/div[1]/div/div/div[3]/div[2]/div/div/div/div[1]/table/tbody/tr[{j}]/td[2]/div/div/div/span/a/b')
            res_id=music.xpath(f'/html/body/div[3]/div[1]/div/div/div[3]/div[2]/div/div/div/div[1]/table/tbody/tr[{j}]/td[2]/div/div/div/span/a')
            for i in res:#获取title，即音乐名
                if i == None:
                    break
                music_name.append(i.get('title'))
            for i in res_id:
                if i == None:
                    break
                i=i.get('href')[9:]
                music_id.append(i)
        return music_name,music_id
    #获取歌手名
    def get_artist_name(self,id:str):
        names=self.etree.HTML(self.get_page_text(id))
        res=names.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/h2')
        name=''
        for i in res:
            i=i.text.strip()
            if i == None:
                break
            name=i
        return name

    def get_music_img(self,ids:[]):
        imgs=[]
        edge_opts = Options()
        edge_opts.add_argument('--headless')
        edge_opts.add_argument('--disable-gpu')
        driver = webdriver.Edge(options=edge_opts)
        for id in ids:
            target=f'https://music.163.com/song?id={id}'
            driver.get(target)
            driver.switch_to.frame(driver.find_element(By.ID, 'g_iframe'))
            page_text = driver.execute_script('return document.documentElement.outerHTML')
            music_img=self.etree.HTML(page_text)
            res=music_img.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[1]/div[1]/img')
            for i in res:
                i=i.get('data-src')
                if i == None:
                    break
                imgs.append(i)
        driver.quit()
        return imgs
    def get_all_info(self, artist_id: str):
        artist_name = self.get_artist_name(artist_id)
        music_name, music_id = self.get_music(artist_id)
        music_image = self.get_music_img(music_id)

        return {
            'artist': artist_name,#字符串
            'title': music_name,#列表
            'external_id': music_id,#列表
            'img_url': music_image,#列表
        }

if __name__ == '__main__':
    kami=GetMusic()
    music_info=kami.get_all_info('35135807')
    print(music_info)
