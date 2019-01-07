#craw_tour.py
#pip install BeautifulSoup4 (실제로 설치할때는 4를 입력해주어야함)
#pip install selenium

#순서는 딱히 중요하진 않지만 가독성을 위해 순서 조절함
import math
import time
from bs4 import BeautifulSoup 
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql 

main_url = "http://tour.interpark.com/" #마지막에 /쓰는건관행적으로
keyword = "파리"

driver = wd.Chrome("C:/chromedriver.exe")
driver.get(main_url)
#time.sleep(3) #무조건 정해진 시간(3초) 쉬는 경우
#사람이 직접 클릭해서 보는정도로 기다리겠다(옵션)
driver.implicitly_wait(10) #명시적 기다리기

#입력란 찾기
elem = driver.find_element_by_id("SearchGNBText")
elem.clear() #내용이 있으면 지우고
elem.send_keys(keyword) #키워드 값 입력
#elem.submit() ->실행안됨, 대부분되는데 지금 인터파크투어에서는 작동이안됨 

#검색단추 찾기 <button class='search-btn'....>
btn_search = driver.find_element_by_css_selector("button.search-btn") 
#class 를 .으로 표현

#클릭
btn_search.click()


######################################################
#에러-반복문안에는 implicity쓰지말기
#driver.implicitly_wait(5)
#반복문 안에서 너무 빨리 작동되어 페이지 로드를 완료 못함

#잘 작동하는 코드1
#time.sleep(5) #절대적인 설정인 타임슬립은 작동 잘됨
#잘 작동되는 코드2
#명시적으로페이지 로드 확인
######################################################


#클릭해서 다음페이지로 넘어가는 조건(oTravelBox의 내용)이 만족되었을 때 쉬는 경우
#특정한 자원(oTravelBox)을 얻으면 바로진행 (효율적임) : 명시적
#지정한 특정 자원만 뜨면 바로 다음으로 진행되기 때문에 더 효율적임
try:
    element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "oTravelBox"))
    )
except Exception as e:
    print("명시적 대기 중 에러", e)

#페이지가 다아 뜨면 바로 진행 (더 간편한 명령어) : 묵시적
driver.implicitly_wait(10) #입력한 값은 최대값인거야

#페이지검사 부분에서 class도 많고 id도 많을때 해당부분 누른상태에서 우클릭 후 copy>copy selector으로 나온 결과에서 복붙
driver.find_element_by_css_selector("div.oTravelBox > ul > li.moreBtnWrap > Button").click() #앞에서 oTravleBox까지 찾아갔으니 그 이후과정들을 복사
time.sleep(3)

span_obj = driver.find_element_by_css_selector("div.panelZone > div.oTravelBox > h4 > span")
str_number = span_obj.text
#print("numbers=", span_obj)
#print("str_numbers=","---" + str_numbers)
#공백이 있으면 제거하기
str_number = str_number.replace("(", "")
str_number = str_number.replace(")", "")
#print("str_numbers=", str_numbers)
number = int(str_number)
#print(type(number))
end = math.ceil(number/10)
#print(end)

tour_list = []
        
def insert_tour(tour):
    conn = pymysql.connect(host='localhost', user='root', password='root', db = 'pythondb', charset='utf8')
    cur = conn.cursor()
    sql = "INSERT INTO tbl_tour(title, link, img, comments, period, depart, price, score, reservation, feature) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(sql, tour)
    conn.commit()
    conn.close()
    print("저장성공")

#페이지 하나씩 찍어보기
try:
    #for page in range(1,end+1):  #전체 다 하려면 이렇게
    for page in range(1,2): #수업 테스트용으로는 1페이지만 보기
        #print(page)
        try:
        #자스크립트실행
        #1페이지까지 이동이 됨
            driver.execute_script("searchModule.SetCategoryList({},'')".format(page))

            time.sleep(3)
            #반복문안에서는 implicitly_wait쓰지 말기
            print("{}페이지로 이동되었습니다.".format(page))
            boxItems = driver.find_elements_by_css_selector("div.panelZone > div.oTravelBox > ul > li")
            #print(len(boxItems))
            #print(boxItems)
            #하나씩 처리
            for li in boxItems:
                #<a onclick=???>
                a_obj = li.find_element_by_css_selector('a')
                #print(a_obj)
                str_links = a_obj.get_attribute('onclick')
                #print(str_links)
                l_list = str_links.split(",")
                str_link = l_list[0]
                str_link = str_link.replace("searchModule.OnClickDetail('","")
                str_link = str_link.replace("'", "")
                #print(str_link)

                #print ('li', li)
                #이미지 객체를 얻어오기
                img = li.find_element_by_css_selector('img')
                #print(img)
                img_src = img.get_attribute('src') #속성얻어오기= get_attribute
                #print(img_src)    
                #제목 가져오기  
                pro_title = li.find_element_by_css_selector(".proTit")
                #print(pro_title)
                str_pro_title = pro_title.text #값얻어오기 = .text
                #print(str_pro_title)
                proSub = li.find_element_by_css_selector(".proSub")
                str_comment = proSub.text
                #print(type(str_comment))
                #print(str_comment)
                proInfos = li.find_elements_by_css_selector(".proInfo")
                obj_period = proInfos[0]
                str_period = obj_period.text
                #print(str_period)
                obj_start = proInfos[1]
                str_start = obj_start.text
                #print(str_start)
                obj_score = proInfos[2]
                str_score = obj_score.text
                #print(str_score)
                #obj_hugi = proInfos[3]
                #str_hugi = obj_hugi.text
                #print(str_hugi)
                proPrice = li.find_element_by_css_selector(".proPrice")
                str_price = proPrice.text
                #print(str_price)
                #튜플에 여행정보를 담는다.
                tour = [str_pro_title, str_link, img_src, str_comment, str_period, str_start, str_price, str_score]
                tour_list.append(tour)
                # print(tour_list)
        except Exception as e:
            print("페이지 파싱 에러", e)

    for tour in tour_list:
        #print(tour)
        link = tour[1]
        driver.get(link)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "lxml")
        #select의 경우는 하나여도 리스트로 리턴
        trs = soup.select("table.ui-data-table > tbody > tr")
        
        #print(trs)
        tr2 = trs[2]
        td = tr2.select("td")[0]
        #td는 [<strong>예약 0 명</strong>, <br/>, '(총 예정인원 10명 / 최소출발 2명)']
        strong = td.contents[0]
        str_reservation = strong.string
        aaa = td.contents[2]
        str_reservation = str_reservation + aaa
        tour.append(str_reservation)
        lis = soup.select(".goods-point > .ui-con-list > li")
        #print(lis)
        str_feature = ""
        for li in lis:
            str_feature = str_feature + li.string + ""
        tour.append(str_feature)
        #데이터베이스 저장
        insert_tour(tour)

    
    #print(len(tour_list))
    print(tour_list)
            


finally :
    driver.close()

    
#db table생성
# CREATE table tbl_tour(
#    num int not null auto_increment, 
#    title varchar(100),
#    link varchar(200),
#    img varchar(200),
#    comments varchar(100),
#    period varchar(20),
#    depart varchar(50),
#    price varchar(50),
#    score varchar(10),
#    reservation varchar(50),
#    feature varchar(200),
#    primary key(num)
# );
