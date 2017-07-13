
# coding: utf-8

# In[7]:


from selenium import webdriver
from bs4 import BeautifulSoup


# In[8]:


main_driver = webdriver.Chrome('chromedriver')
sub_driver = webdriver.Chrome('chromedriver')
#driver.implicitly_wait(3)


# In[9]:


main_driver.get('https://www.ncbi.nlm.nih.gov/pubmed/?term=hasstructuredabstract')


# In[10]:


for i in range(0, 181260, 1) :
    pmid_list = BeautifulSoup(main_driver.page_source, 'html.parser').select('.rprtid dd')

    for pmid in pmid_list :
        sub_driver.get('https://www.ncbi.nlm.nih.gov/pubmed/' + pmid.text.strip() + '?report=xml&format=text')
        xml = BeautifulSoup(BeautifulSoup(sub_driver.page_source, 'html.parser').find('pre').text, 'html.parser')

        for node in xml.findAll('abstracttext') :
            print(node['label'])
            print(node.text)
            
        print('\n')
    main_driver.find_element_by_class_name('next').click()

