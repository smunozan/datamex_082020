def time_classification(x):
    try:
        hora = int(x["Time"][0:1])
        if hora >= 00 and hora < 06:
            return "00h00 - 06h00
        else:
            return "otra hora"
    except:
        return x
    
def prueba_2():
    print("hola")