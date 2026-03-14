"""
Car database — all brands & models with resale curve (yr1..yr5 % of ex-showroom) and engine class.
eng: small (<1000cc) | mid (1000-1500cc) | large (>1500cc/SUV)
Source: Autocar-Spinny 2024 data + IRDAI + industry benchmarks
"""

CAR_DB = {
    "Maruti Suzuki": {
        "brandResale": [0.82, 0.72, 0.63, 0.55, 0.48], "brandEng": "small",
        "models": {
            "Alto K10": {"resale": [0.80, 0.69, 0.60, 0.52, 0.45], "eng": "small"},
            "S-Presso": {"resale": [0.80, 0.69, 0.60, 0.52, 0.45], "eng": "small"},
            "Wagon R": {"resale": [0.83, 0.73, 0.64, 0.56, 0.49], "eng": "small"},
            "Celerio": {"resale": [0.81, 0.71, 0.62, 0.54, 0.47], "eng": "small"},
            "Swift": {"resale": [0.85, 0.76, 0.67, 0.59, 0.52], "eng": "mid"},
            "Baleno": {"resale": [0.83, 0.73, 0.64, 0.56, 0.50], "eng": "mid"},
            "Fronx": {"resale": [0.83, 0.73, 0.65, 0.57, 0.50], "eng": "mid"},
            "Dzire": {"resale": [0.85, 0.75, 0.67, 0.59, 0.52], "eng": "mid"},
            "Ciaz": {"resale": [0.80, 0.70, 0.61, 0.53, 0.46], "eng": "mid"},
            "Brezza": {"resale": [0.84, 0.74, 0.65, 0.57, 0.50], "eng": "mid"},
            "Grand Vitara": {"resale": [0.82, 0.72, 0.63, 0.55, 0.48], "eng": "mid"},
            "Victoris": {"resale": [0.83, 0.73, 0.65, 0.57, 0.51], "eng": "mid"},
            "e Vitara": {"resale": [0.78, 0.67, 0.58, 0.50, 0.43], "eng": "mid"},
            "Jimny": {"resale": [0.82, 0.72, 0.63, 0.56, 0.49], "eng": "mid"},
            "Ertiga": {"resale": [0.83, 0.73, 0.65, 0.57, 0.50], "eng": "mid"},
            "XL6": {"resale": [0.83, 0.73, 0.65, 0.57, 0.50], "eng": "mid"},
            "Invicto": {"resale": [0.83, 0.73, 0.65, 0.57, 0.50], "eng": "large"},
            "Eeco": {"resale": [0.82, 0.72, 0.63, 0.55, 0.48], "eng": "small"},
        },
    },
    "Hyundai": {
        "brandResale": [0.80, 0.70, 0.61, 0.53, 0.46], "brandEng": "mid",
        "models": {
            "Grand i10 Nios": {"resale": [0.79, 0.69, 0.60, 0.52, 0.45], "eng": "small"},
            "i20": {"resale": [0.81, 0.71, 0.62, 0.55, 0.48], "eng": "mid"},
            "Exter": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "small"},
            "Venue": {"resale": [0.81, 0.71, 0.63, 0.55, 0.48], "eng": "mid"},
            "Creta": {"resale": [0.83, 0.73, 0.65, 0.57, 0.50], "eng": "mid"},
            "Creta Electric": {"resale": [0.77, 0.66, 0.57, 0.49, 0.42], "eng": "large"},
            "Alcazar": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "large"},
            "Verna": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
            "Aura": {"resale": [0.79, 0.69, 0.61, 0.53, 0.46], "eng": "mid"},
            "Tucson": {"resale": [0.78, 0.68, 0.59, 0.52, 0.45], "eng": "large"},
            "Ioniq 5": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "large"},
            "Ioniq 6": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "large"},
        },
    },
    "Tata": {
        "brandResale": [0.78, 0.67, 0.58, 0.51, 0.44], "brandEng": "mid",
        "models": {
            "Tiago": {"resale": [0.78, 0.68, 0.59, 0.52, 0.45], "eng": "small"},
            "Tiago EV": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "small"},
            "Tigor": {"resale": [0.78, 0.67, 0.59, 0.51, 0.44], "eng": "small"},
            "Tigor EV": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "small"},
            "Altroz": {"resale": [0.79, 0.69, 0.60, 0.53, 0.46], "eng": "mid"},
            "Punch": {"resale": [0.81, 0.71, 0.62, 0.55, 0.48], "eng": "small"},
            "Punch EV": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "small"},
            "Nexon": {"resale": [0.82, 0.72, 0.63, 0.56, 0.49], "eng": "mid"},
            "Nexon EV": {"resale": [0.76, 0.65, 0.56, 0.48, 0.41], "eng": "mid"},
            "Harrier": {"resale": [0.79, 0.69, 0.61, 0.53, 0.46], "eng": "large"},
            "Harrier EV": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
            "Safari": {"resale": [0.79, 0.69, 0.61, 0.53, 0.46], "eng": "large"},
            "Safari EV": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "large"},
            "Curvv": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
            "Curvv EV": {"resale": [0.76, 0.65, 0.56, 0.48, 0.41], "eng": "mid"},
            "Sierra": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
            "Sierra EV": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "large"},
            "Avinya EV": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "large"},
        },
    },
    "Mahindra": {
        "brandResale": [0.79, 0.69, 0.60, 0.53, 0.46], "brandEng": "large",
        "models": {
            "KUV100 NXT": {"resale": [0.76, 0.66, 0.57, 0.50, 0.43], "eng": "small"},
            "Bolero": {"resale": [0.82, 0.72, 0.63, 0.55, 0.48], "eng": "large"},
            "Bolero Neo": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "large"},
            "Thar": {"resale": [0.84, 0.74, 0.66, 0.58, 0.51], "eng": "mid"},
            "Thar Roxx": {"resale": [0.83, 0.73, 0.65, 0.57, 0.50], "eng": "large"},
            "XUV 3XO": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
            "XUV 3XO EV": {"resale": [0.76, 0.65, 0.56, 0.48, 0.41], "eng": "mid"},
            "Scorpio N": {"resale": [0.81, 0.71, 0.63, 0.55, 0.48], "eng": "large"},
            "Scorpio Classic": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "large"},
            "XUV700": {"resale": [0.82, 0.72, 0.64, 0.56, 0.49], "eng": "large"},
            "XUV 7XO": {"resale": [0.81, 0.71, 0.63, 0.55, 0.48], "eng": "large"},
            "BE 6": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
            "XEV 9e": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "large"},
            "XEV 7e": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "large"},
            "XUV 9S": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
        },
    },
    "Toyota": {
        "brandResale": [0.83, 0.73, 0.65, 0.57, 0.51], "brandEng": "large",
        "models": {
            "Glanza": {"resale": [0.82, 0.72, 0.63, 0.55, 0.48], "eng": "mid"},
            "Urban Cruiser Hyryder": {"resale": [0.83, 0.73, 0.64, 0.56, 0.50], "eng": "mid"},
            "Urban Cruiser EV": {"resale": [0.78, 0.67, 0.58, 0.50, 0.43], "eng": "large"},
            "Taisor": {"resale": [0.82, 0.72, 0.63, 0.55, 0.49], "eng": "mid"},
            "Rumion": {"resale": [0.83, 0.73, 0.65, 0.57, 0.50], "eng": "mid"},
            "Innova Crysta": {"resale": [0.86, 0.77, 0.69, 0.61, 0.54], "eng": "large"},
            "Innova HyCross": {"resale": [0.85, 0.76, 0.68, 0.60, 0.53], "eng": "large"},
            "Fortuner": {"resale": [0.87, 0.78, 0.70, 0.62, 0.55], "eng": "large"},
            "Camry": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "large"},
            "Vellfire": {"resale": [0.80, 0.70, 0.62, 0.55, 0.48], "eng": "large"},
            "Hilux": {"resale": [0.82, 0.72, 0.64, 0.56, 0.49], "eng": "large"},
            "Land Cruiser": {"resale": [0.85, 0.76, 0.68, 0.61, 0.54], "eng": "large"},
        },
    },
    "Honda": {
        "brandResale": [0.79, 0.69, 0.61, 0.53, 0.46], "brandEng": "mid",
        "models": {
            "Amaze": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
            "City": {"resale": [0.81, 0.71, 0.63, 0.55, 0.48], "eng": "mid"},
            "City Hybrid": {"resale": [0.82, 0.72, 0.64, 0.56, 0.49], "eng": "mid"},
            "Elevate": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
        },
    },
    "Kia": {
        "brandResale": [0.79, 0.69, 0.61, 0.53, 0.46], "brandEng": "mid",
        "models": {
            "Sonet": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
            "Syros": {"resale": [0.80, 0.70, 0.62, 0.54, 0.47], "eng": "mid"},
            "Seltos": {"resale": [0.81, 0.71, 0.63, 0.55, 0.48], "eng": "mid"},
            "Carens": {"resale": [0.79, 0.69, 0.61, 0.53, 0.46], "eng": "mid"},
            "EV6": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "large"},
            "EV9": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "large"},
        },
    },
    "MG Motor": {
        "brandResale": [0.76, 0.66, 0.57, 0.49, 0.43], "brandEng": "large",
        "models": {
            "Hector": {"resale": [0.77, 0.67, 0.58, 0.51, 0.44], "eng": "large"},
            "Hector Plus": {"resale": [0.77, 0.67, 0.58, 0.51, 0.44], "eng": "large"},
            "Astor": {"resale": [0.76, 0.66, 0.58, 0.50, 0.43], "eng": "mid"},
            "ZS EV": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "large"},
            "Comet EV": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "small"},
            "Windsor EV": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "mid"},
            "Gloster": {"resale": [0.77, 0.67, 0.59, 0.51, 0.44], "eng": "large"},
            "Majestor": {"resale": [0.76, 0.66, 0.57, 0.49, 0.43], "eng": "large"},
        },
    },
    "Skoda": {
        "brandResale": [0.77, 0.67, 0.58, 0.50, 0.43], "brandEng": "mid",
        "models": {
            "Kylaq": {"resale": [0.79, 0.69, 0.60, 0.52, 0.45], "eng": "mid"},
            "Kushaq": {"resale": [0.78, 0.68, 0.59, 0.51, 0.44], "eng": "mid"},
            "Slavia": {"resale": [0.77, 0.67, 0.59, 0.51, 0.44], "eng": "mid"},
            "Kodiaq": {"resale": [0.77, 0.67, 0.58, 0.51, 0.44], "eng": "large"},
            "Superb": {"resale": [0.76, 0.66, 0.57, 0.50, 0.43], "eng": "large"},
            "Enyaq iV": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "large"},
        },
    },
    "Volkswagen": {
        "brandResale": [0.77, 0.67, 0.58, 0.50, 0.43], "brandEng": "mid",
        "models": {
            "Taigun": {"resale": [0.78, 0.68, 0.59, 0.51, 0.44], "eng": "mid"},
            "Virtus": {"resale": [0.77, 0.67, 0.59, 0.51, 0.44], "eng": "mid"},
            "Tiguan": {"resale": [0.77, 0.67, 0.58, 0.50, 0.43], "eng": "large"},
            "Tayron": {"resale": [0.77, 0.67, 0.58, 0.50, 0.43], "eng": "large"},
            "ID.4": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "large"},
        },
    },
    "Jeep": {
        "brandResale": [0.77, 0.67, 0.59, 0.51, 0.44], "brandEng": "large",
        "models": {
            "Meridian": {"resale": [0.78, 0.68, 0.60, 0.52, 0.45], "eng": "large"},
            "Compass": {"resale": [0.78, 0.68, 0.60, 0.52, 0.45], "eng": "large"},
            "Wrangler": {"resale": [0.80, 0.70, 0.62, 0.55, 0.48], "eng": "large"},
        },
    },
    "Renault": {
        "brandResale": [0.75, 0.65, 0.56, 0.48, 0.41], "brandEng": "small",
        "models": {
            "Kwid": {"resale": [0.75, 0.65, 0.56, 0.49, 0.42], "eng": "small"},
            "Kiger": {"resale": [0.76, 0.66, 0.57, 0.49, 0.42], "eng": "small"},
            "Duster": {"resale": [0.78, 0.68, 0.59, 0.51, 0.44], "eng": "mid"},
        },
    },
    "Nissan": {
        "brandResale": [0.76, 0.66, 0.57, 0.49, 0.42], "brandEng": "small",
        "models": {
            "Magnite": {"resale": [0.77, 0.67, 0.58, 0.50, 0.43], "eng": "small"},
            "Gravite": {"resale": [0.77, 0.67, 0.58, 0.50, 0.43], "eng": "mid"},
            "X-Trail": {"resale": [0.77, 0.67, 0.58, 0.50, 0.43], "eng": "mid"},
            "Tekton": {"resale": [0.77, 0.67, 0.58, 0.50, 0.43], "eng": "mid"},
        },
    },
    "Citroen": {
        "brandResale": [0.73, 0.62, 0.53, 0.45, 0.38], "brandEng": "mid",
        "models": {
            "C3": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "small"},
            "eC3": {"resale": [0.71, 0.60, 0.51, 0.43, 0.36], "eng": "small"},
            "C3 Aircross": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "mid"},
            "C5 Aircross": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "large"},
        },
    },
    "BYD": {
        "brandResale": [0.71, 0.60, 0.51, 0.43, 0.36], "brandEng": "large",
        "models": {
            "Atto 3": {"resale": [0.71, 0.60, 0.51, 0.43, 0.36], "eng": "large"},
            "Seal": {"resale": [0.71, 0.60, 0.51, 0.43, 0.36], "eng": "large"},
            "Sealion 6": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "large"},
            "Sealion 7": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "large"},
        },
    },
    "Porsche": {
        "brandResale": [0.77, 0.67, 0.58, 0.51, 0.44], "brandEng": "large",
        "models": {
            "Cayenne": {"resale": [0.77, 0.67, 0.58, 0.51, 0.44], "eng": "large"},
            "Macan": {"resale": [0.76, 0.66, 0.57, 0.50, 0.43], "eng": "large"},
            "Taycan": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "large"},
            "911": {"resale": [0.80, 0.71, 0.63, 0.56, 0.50], "eng": "large"},
        },
    },
    "Land Rover": {
        "brandResale": [0.72, 0.61, 0.52, 0.44, 0.37], "brandEng": "large",
        "models": {
            "Defender": {"resale": [0.74, 0.63, 0.54, 0.47, 0.40], "eng": "large"},
            "Discovery Sport": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "large"},
            "Range Rover": {"resale": [0.74, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
            "Range Rover Sport": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "large"},
        },
    },
    "BMW": {
        "brandResale": [0.76, 0.65, 0.56, 0.48, 0.41], "brandEng": "large",
        "models": {
            "3 Series": {"resale": [0.76, 0.65, 0.56, 0.48, 0.41], "eng": "large"},
            "5 Series": {"resale": [0.75, 0.64, 0.55, 0.48, 0.41], "eng": "large"},
            "X1": {"resale": [0.77, 0.66, 0.57, 0.49, 0.42], "eng": "large"},
            "X3": {"resale": [0.77, 0.67, 0.58, 0.50, 0.43], "eng": "large"},
            "X5": {"resale": [0.78, 0.68, 0.59, 0.51, 0.44], "eng": "large"},
            "iX": {"resale": [0.72, 0.61, 0.52, 0.44, 0.37], "eng": "large"},
        },
    },
    "Mercedes-Benz": {
        "brandResale": [0.75, 0.64, 0.55, 0.47, 0.40], "brandEng": "large",
        "models": {
            "A-Class": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
            "C-Class": {"resale": [0.76, 0.65, 0.56, 0.48, 0.41], "eng": "large"},
            "E-Class": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
            "GLA": {"resale": [0.76, 0.65, 0.56, 0.48, 0.41], "eng": "large"},
            "GLC": {"resale": [0.76, 0.66, 0.57, 0.49, 0.42], "eng": "large"},
            "GLE": {"resale": [0.77, 0.66, 0.57, 0.49, 0.42], "eng": "large"},
            "EQS": {"resale": [0.70, 0.59, 0.50, 0.42, 0.35], "eng": "large"},
        },
    },
    "Audi": {
        "brandResale": [0.74, 0.63, 0.54, 0.46, 0.39], "brandEng": "large",
        "models": {
            "A4": {"resale": [0.74, 0.63, 0.54, 0.46, 0.39], "eng": "large"},
            "A6": {"resale": [0.73, 0.62, 0.53, 0.45, 0.38], "eng": "large"},
            "Q3": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
            "Q5": {"resale": [0.75, 0.64, 0.55, 0.47, 0.40], "eng": "large"},
            "Q7": {"resale": [0.76, 0.65, 0.56, 0.48, 0.41], "eng": "large"},
            "e-tron": {"resale": [0.70, 0.59, 0.50, 0.42, 0.35], "eng": "large"},
        },
    },
    "Volvo": {
        "brandResale": [0.74, 0.63, 0.54, 0.47, 0.40], "brandEng": "large",
        "models": {
            "XC40": {"resale": [0.74, 0.63, 0.55, 0.47, 0.40], "eng": "large"},
            "XC60": {"resale": [0.75, 0.64, 0.56, 0.48, 0.41], "eng": "large"},
            "XC90": {"resale": [0.76, 0.65, 0.57, 0.49, 0.42], "eng": "large"},
            "C40 Recharge": {"resale": [0.71, 0.60, 0.51, 0.43, 0.36], "eng": "large"},
        },
    },
    "Other / Custom": {
        "brandResale": [0.78, 0.67, 0.58, 0.50, 0.43], "brandEng": "mid",
        "models": {
            "Custom / Not Listed": {"resale": [0.78, 0.67, 0.58, 0.50, 0.43], "eng": "mid"},
        },
    },
}

RESALE_EXT = {
    "petrol": [0.85, 0.76, 0.67, 0.59, 0.52, 0.45, 0.39, 0.34, 0.29, 0.25, 0.21, 0.18, 0.15, 0.13, 0.11],
    "diesel": [0.84, 0.75, 0.66, 0.58, 0.51, 0.44, 0.38, 0.33, 0.28, 0.24, 0.21, 0.18, 0.15, 0.13, 0.11],
    "cng": [0.83, 0.73, 0.64, 0.56, 0.49, 0.42, 0.36, 0.31, 0.27, 0.23, 0.20, 0.17, 0.14, 0.12, 0.10],
    "ev": [0.82, 0.70, 0.60, 0.52, 0.45, 0.37, 0.31, 0.26, 0.22, 0.18, 0.15, 0.12, 0.10, 0.08, 0.07],
    "strong_hybrid": [0.84, 0.75, 0.66, 0.59, 0.52, 0.46, 0.40, 0.35, 0.30, 0.26, 0.22, 0.19, 0.16, 0.14, 0.12],
}


def get_brands():
    return sorted(CAR_DB.keys())


def get_models(brand: str):
    if brand not in CAR_DB:
        return []
    return list(CAR_DB[brand]["models"].keys())


def get_model_info(brand: str, model: str):
    """Return model dict with resale + eng, or None."""
    if brand in CAR_DB and model in CAR_DB[brand]["models"]:
        return CAR_DB[brand]["models"][model]
    return None


BASELINE_ANN_KM = 12_000

def _mileage_factor(ann_km: float, year: int) -> float:
    """
    Mileage adjustment for resale value.
    Baseline: 12,000 km/year (Indian market standard).
    High-km cars (>12k/yr) lose extra value; low-km cars retain more.
    The effect compounds slightly with age because older high-km cars have
    proportionally more wear.
    Factor is clamped to [0.80, 1.12] to avoid extreme swings.
    """
    if ann_km <= 0:
        ann_km = BASELINE_ANN_KM
    deviation = (ann_km / BASELINE_ANN_KM) - 1.0
    age_scale = 1.0 + 0.02 * (year - 1)
    factor = 1.0 - 0.10 * deviation * age_scale
    return max(0.80, min(1.12, factor))


EV_DEGRADATION_PENALTY = {
    5: -0.03, 6: -0.03, 7: -0.03, 8: -0.03, 9: -0.03,
    10: -0.04, 11: -0.04, 12: -0.04, 13: -0.04, 14: -0.04,
}


def _extend_to_15(base5: list[float], fuel_ext: list[float]) -> list[float]:
    """Extend a 5-year resale array to 15 years using decay ratios from the fuel-type curve.
    This matches the legacy extendTo15 approach."""
    arr = list(base5)
    for i in range(5, 15):
        decay = fuel_ext[i] / fuel_ext[i - 1] if fuel_ext[i - 1] else 0.85
        arr.append(round(arr[-1] * decay, 3))
    return arr


def get_resale_array(
    brand: str | None, model: str | None, fuel: str,
    ann_km: float = BASELINE_ANN_KM,
) -> tuple[list[float], str, str]:
    """Return (resale_pct_arr[0..14] for year 1..15, resale_src_label, eng).
    Resale percentages are adjusted for annual kilometers driven.
    Uses legacy decay-ratio extension for model/brand-specific curves."""
    fuel_key = fuel if fuel in RESALE_EXT else "petrol"
    base_ext = RESALE_EXT[fuel_key]
    eng = "mid"
    src = f"{fuel_key.upper()} fuel-type curve"

    if brand and brand in CAR_DB:
        eng = CAR_DB[brand]["brandEng"]
        if model and model in CAR_DB[brand]["models"]:
            m = CAR_DB[brand]["models"][model]
            ext = _extend_to_15(m["resale"], base_ext)
            eng = m["eng"]
            src = f"{brand} {model} (model)"
        else:
            ext = _extend_to_15(CAR_DB[brand]["brandResale"], base_ext)
            src = f"{brand} (brand avg)"
    else:
        ext = list(base_ext)

    if fuel == "ev":
        for i in range(len(ext)):
            penalty = EV_DEGRADATION_PENALTY.get(i, 0)
            if penalty:
                ext[i] = max(0.05, round(ext[i] * (1 + penalty), 4))

    adjusted = []
    for yr_idx, pct in enumerate(ext):
        mf = _mileage_factor(ann_km, yr_idx + 1)
        adj = round(pct * mf, 4)
        if adjusted:
            adj = min(adj, adjusted[-1])
        adjusted.append(max(0.03, adj))

    return adjusted, src, eng
