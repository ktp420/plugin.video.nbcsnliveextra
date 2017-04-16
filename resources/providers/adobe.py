from resources.globals import *


class ADOBE():    
    def __init__(self, requestor_id='nbcsports'):
        self.requestor_id = requestor_id

    def GET_IDP(self):
        if not os.path.exists(ADDON_PATH_PROFILE):
            os.makedirs(ADDON_PATH_PROFILE)
        
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))
        
        #IDP_URL= 'https://sp.auth.adobe.com/adobe-services/authenticate?requestor_id=nbcsports&redirect_url=http://stream.nbcsports.com/nbcsn/index_nbcsn-generic.html?referrer=http://stream.nbcsports.com/liveextra/&domain_name=stream.nbcsports.com&mso_id=TWC&noflash=true&no_iframe=true'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Language", "en-us"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),
                            ("User-Agent", UA_IPHONE)]
        
        resp = opener.open(IDP_URL)
        idp_source = resp.read()
        resp.close()
        #print idp_source
        #cj.save(ignore_discard=True);                
        SAVE_COOKIE(cj)

        idp_source = idp_source.replace('\n',"")        

        saml_request = FIND(idp_source,'<input type="hidden" name="SAMLRequest" value="','"')
        print saml_request

        relay_state = FIND(idp_source,'<input type="hidden" name="RelayState" value="','"')

        saml_submit_url = FIND(idp_source,'action="','"')

        
        print saml_submit_url
        #print relay_state
        return saml_request, relay_state, saml_submit_url

    def POST_ASSERTION_CONSUMER_SERVICE(self,saml_response,relay_state):
        ###################################################################
        # SAML Assertion Consumer
        ###################################################################        
        if 'skip' == saml_response: return
        url = 'https://sp.auth.adobe.com/sp/saml/SAMLAssertionConsumer'
        
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        opener.addheaders = [("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            #("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),
                            ("Origin", ORIGIN),
                            ("Referer", REFERER),
                            #("Cookie", cookies),
                            ("User-Agent", UA_IPHONE)]


        body = urllib.urlencode({'SAMLResponse' : saml_response,
                                 'RelayState' : relay_state
                                 })

        request = urllib2.Request(url, body)
        response = opener.open(request)
        content = response.read()
        response.close()
        SAVE_COOKIE(cj)
        log('POST_ASSERTION_CONSUMER_SERVICE------------------------------------------------')
        log(str(opener.addheaders))
        log(str(body))
        log(str(response.getcode()))
        log(str(content))
        log('-------------------------------------------------------------------------------')
        
    

    def POST_SESSION_DEVICE(self,signed_requestor_id):
        ###################################################################
        # Create a Session for Device
        ###################################################################                
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        url = 'https://sp.auth.adobe.com//adobe-services/1.0/sessionDevice'        
        opener.addheaders = [ ("Accept", "*/*"),
                    ("Accept-Encoding", "gzip, deflate"),
                    ("Accept-Language", "en-us"),
                    ("Content-Type", "application/x-www-form-urlencoded"),
                    ("Proxy-Connection", "keep-alive"),
                    ("Connection", "keep-alive"),                                                
                    #("Cookie", cookies),
                    ("User-Agent", UA_ADOBE_PASS)]
        
        data = urllib.urlencode({'requestor_id' : self.requestor_id,
                                 '_method' : 'GET',
                                 'signed_requestor_id' : signed_requestor_id,
                                 'device_id' : DEVICE_ID
                                })
        
                
        request = urllib2.Request(url, data)
        response = opener.open(request)
        content = response.read()
        response.close()
        SAVE_COOKIE(cj)
        log('POST_SESSION_DEVICE------------------------------------------------------------')
        log(str(headers))
        log(str(data))
        log(str(response))
        log(str(content))
        log('-------------------------------------------------------------------------------')
        
        auth_token = FIND(content,'<authnToken>','</authnToken>')
        log("AUTH TOKEN")
        log(str(auth_token))
        auth_token = auth_token.replace("&lt;", "<")
        auth_token = auth_token.replace("&gt;", ">")
        # this has to be last:
        auth_token = auth_token.replace("&amp;", "&")
        log(auth_token)

        #Save auth token to file for         
        fname = os.path.join(ADDON_PATH_PROFILE, 'auth.token')
        #if not os.path.isfile(fname):            
        device_file = open(fname,'w')   
        device_file.write(auth_token)
        device_file.close()

        #return auth_token, session_guid        
   

    def POST_AUTHORIZE_DEVICE(self,resource_id,signed_requestor_id):
        ###################################################################
        # Authorize Device
        ###################################################################
        fname = os.path.join(ADDON_PATH_PROFILE, 'auth.token')
        device_file = open(fname,'r') 
        auth_token = device_file.readline()
        device_file.close()
        
        if auth_token == '':
            return ''

        url = 'https://sp.auth.adobe.com//adobe-services/1.0/authorizeDevice'
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [ ("Accept", "*/*"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),
                            #("Cookie", cookies),
                            ("User-Agent", UA_ADOBE_PASS)]

        data = urllib.urlencode({'requestor_id' : self.requestor_id,
                                 'resource_id' : resource_id,
                                 'signed_requestor_id' : signed_requestor_id,
                                 'mso_id' : MSO_ID,
                                 'authentication_token' : auth_token,
                                 'device_id' : DEVICE_ID,
                                 'userMeta' : '1'                             
                                })
        
        print data
        request = urllib2.Request(url, data)
        response = opener.open(request)
        content = response.read()
        response.close()
        SAVE_COOKIE(cj)

        log(content)        
        print response

        authz = FIND(content,'<authzToken>','</authzToken>')                
        authz = authz.replace("&lt;", "<")
        authz = authz.replace("&gt;", ">")
        # this has to be last:
        authz = authz.replace("&amp;", "&")
        print "AUTH Z TOKEN"
        print authz
        
        return authz


    def POST_SHORT_AUTHORIZED(self,signed_requestor_id,authz):
        ###################################################################
        # Short Authorize Device
        ###################################################################
        fname = os.path.join(ADDON_PATH_PROFILE, 'auth.token')
        device_file = open(fname,'r') 
        auth_token = device_file.readline()
        device_file.close()

        session_guid = FIND(auth_token,'<simpleTokenAuthenticationGuid>','</simpleTokenAuthenticationGuid>')
        print "SESSION GUID"
        print session_guid    

        url = 'https://sp.auth.adobe.com//adobe-services/1.0/deviceShortAuthorize'
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [ ("Accept", "*/*"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),                                                                            
                            ("User-Agent", UA_ADOBE_PASS)]
        

        data = urllib.urlencode({'requestor_id' : self.requestor_id,                             
                                 'signed_requestor_id' : signed_requestor_id,
                                 'mso_id' : MSO_ID,
                                 'session_guid' : session_guid,
                                 'hashed_guid' : 'false',
                                 'authz_token' : authz,
                                 'device_id' : DEVICE_ID
                                })

        resp = opener.open(url, data)
        media_token = resp.read()
        resp.close()    
        print media_token

        return media_token

    def TV_SIGN(self, media_token, resource_id, stream_url):    
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        #print cj
        cookies = ''
        for cookie in cj:        
            if cookie.name == "BIGipServerAdobe_Pass_Prod" or cookie.name == "JSESSIONID":
                cookies = cookies + cookie.name + "=" + cookie.value + "; "

        url = 'http://sp.auth.adobe.com//tvs/v1/sign'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [ ("Accept", "*/*"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en;q=1"),
                            ("Content-Type", "application/x-www-form-urlencoded"),                                                                                         
                            ("Cookie", cookies),
                            ("User-Agent", "NBCSports/4.2.0 (iPhone; iOS 8.3; Scale/2.00)")]
        

        data = urllib.urlencode({'cdn' : 'akamai',
                                 'mediaToken' : base64.b64encode(media_token),
                                 'resource' : base64.b64encode(resource_id),
                                 'url' : stream_url
                                })

        resp = opener.open(url, data)
        url = resp.read()
        resp.close()    
        
        return url
        
