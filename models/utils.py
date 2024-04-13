import httpx,base64
from fastapi import HTTPException
from urllib.parse import unquote

BASE = 'http://localhost:8000'

async def default():
    return ''

async def error(err:str):
    # TODO
    #    return {
    #        "status":500,
    #        "info":err,
    #        "sources":[]
    #    }
    print(err) # for understanding whats gone wrong in the deployment.viewable in vercel logs.
    return {}
async def decode_url(encrypted_source_url:str,VIDSRC_KEY:str):
    standardized_input = encrypted_source_url.replace('_', '/').replace('-', '+')
    binary_data = base64.b64decode(standardized_input)
    encoded = bytearray(binary_data)
    key_bytes = bytes(VIDSRC_KEY, 'utf-8')
    j = 0
    s = bytearray(range(256))

    for i in range(256):
      j = (j + s[i] + key_bytes[i % len(key_bytes)]) & 0xff
      s[i], s[j] = s[j], s[i]

    decoded = bytearray(len(encoded))
    i = 0
    k = 0
    for index in range(len(encoded)):
      i = (i + 1) & 0xff
      k = (k + s[i]) & 0xff
      s[i], s[k] = s[k], s[i]
      t = (s[i] + s[k]) & 0xff
      decoded[index] = encoded[index] ^ s[t]
    decoded_text = decoded.decode('utf-8')
    return unquote(decoded_text)

async def fetch(url:str,headers:dict={},method:str="GET",data=None,redirects:bool=True):
    async with httpx.AsyncClient(follow_redirects=redirects) as client:
        if method=="GET":
            response = await client.get(url,headers=headers)
            return response
        if method=="POST":
            response = await client.post(url,headers=headers,data=data)
            return response
        else:
            return "ERROR"
            
class Utilities:
    @staticmethod
    def decode_src(encoded, seed) -> str:
        encoded_buffer = bytes.fromhex(encoded)
        decoded = ""
        for i in range(len(encoded_buffer)):
            decoded += chr(encoded_buffer[i] ^ ord(seed[i % len(seed)]))
        return decoded

    @staticmethod
    def hunter(h, u, n, t, e, r) -> str:
        def hunter_def(d, e, f) -> int:
            charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
            source_base = charset[0:e]
            target_base = charset[0:f]

            reversed_input = list(d)[::-1]
            result = 0

            for power, digit in enumerate(reversed_input):
                if digit in source_base:
                    result += source_base.index(digit) * e**power

            converted_result = ""
            while result > 0:
                converted_result = target_base[result % f] + converted_result
                result = (result - (result % f)) // f

            return int(converted_result) or 0
        
        i = 0
        result_str = ""
        while i < len(h):
            j = 0
            s = ""
            while h[i] != n[e]:
                s += h[i]
                i += 1

            while j < len(n):
                s = s.replace(n[j], str(j))
                j += 1

            result_str += chr(hunter_def(s, e, 10) - t)
            i += 1

        return result_str

    @staticmethod
    def decode_base64_url_safe(s: str) -> bytearray:
        standardized_input = s.replace('_', '/').replace('-', '+')
        binary_data = base64.b64decode(standardized_input)
        return bytearray(binary_data)
        
