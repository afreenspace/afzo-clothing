from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, hashlib, os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'afzo_secret_key_2024'

DB = 'database.db'
ADMIN_EMAIL = 'admin@afzo.com'
ADMIN_PASSWORD = 'afzo2024'
DISCOUNT_CODE = 'AFZO20'

PRODUCTS = [
    {"id":1,"name":"Linen Summer Dress","price":2499,"category":"summer","stock":14,"image":"/static/images/products/top5.jpg","desc":"Effortless linen blend, perfect for warm afternoons. Relaxed silhouette with adjustable waist tie.","colors":["#C4A882","#E8D5C0","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":2,"name":"Structured Blazer","price":4299,"category":"jackets","stock":6,"image":"/static/images/products/top9.jpg","desc":"Tailored to perfection. A wardrobe essential that transitions from office to evening effortlessly.","colors":["#2C2C2C","#C4A882","#8B7355"],"sizes":["XS","S","M","L"],"outfit_type":"top"},
    {"id":3,"name":"Sage Green Suede Lace Sneakers","price":1299,"category":"shoes","stock":8,"image":"/static/images/products/shoe1.jpg","desc":"Dreamy sage green suede sneakers with delicate lace ribbon ties. Y2K-inspired silhouette with gum sole. The must-have sneaker for feminine streetwear and cottagecore looks.","colors":["#C4A882","#2C2C2C","#F5F0EB"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},
    {"id":4,"name":"Wide Leg Trousers","price":2799,"category":"collections","stock":3,"image":"/static/images/products/top4.jpg","desc":"High-rise wide-leg silhouette in fluid crepe fabric. Sophisticated and comfortable.","colors":["#E8D5C0","#2C2C2C","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":5,"name":"Brown Monogram Tote Bag","price":1299,"category":"accessories","stock":20,"image":"/static/images/products/acc1.jpg","desc":"Minimalist brushed gold cuff. Statement piece that elevates any outfit.","colors":["#D4AF37","#C0C0C0"],"sizes":["One Size"],"outfit_type":"accessory"},
    {"id":6,"name":"Oversized Trench","price":5499,"category":"jackets","stock":2,"image":"/static/images/products/top8.jpg","desc":"The definitive trench coat. Oversized fit with classic storm flap and D-ring belt.","colors":["#C4A882","#2C2C2C","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":7,"name":"Green Bow Platform Sandals","price":899,"category":"shoes","stock":11,"image":"/static/images/products/shoe2.jpg","desc":"Cute sage green ribbed bow flat sandals with a platform sole. Lightweight and summer-ready. Perfect for casual days, beach outings and brunch dates.","colors":["#C4A882","#F5F0EB","#2C2C2C"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},
    {"id":8,"name":"Silk Cami Top","price":1999,"category":"summer","stock":18,"image":"/static/images/products/top1.jpg","desc":"Pure silk camisole with delicate lace trim. Layer it or let it stand alone.","colors":["#E8D5C0","#C4A882","#2C2C2C","#F5F0EB"],"sizes":["XS","S","M","L"],"outfit_type":"top"},
    {"id":9,"name":"Black Canvas Crossbody Bag","price":699,"category":"accessories","stock":5,"image":"/static/images/products/acc2.jpg","desc":"Spacious vegetable-tanned leather tote. Ages beautifully with every use.","colors":["#C4A882","#2C2C2C","#8B7355"],"sizes":["One Size"],"outfit_type":"accessory"},
    {"id":10,"name":"Floral Midi Dress","price":3399,"category":"collections","stock":9,"image":"/static/images/products/top6.jpg","desc":"Romantic floral print on a flowing midi silhouette. Feminine and effortlessly chic.","colors":["#E8D5C0","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":11,"name":"Knit Cardigan","price":2499,"category":"collections","stock":4,"image":"/static/images/products/top3.jpg","desc":"Relaxed-fit merino wool cardigan. Cozy, refined, effortlessly wearable.","colors":["#E8D5C0","#C4A882","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":12,"name":"Silver Figaro Chain Necklace","price":899,"category":"accessories","stock":25,"image":"/static/images/products/acc3.jpg","desc":"Freshwater pearl drop earrings with 14k gold fill. Timeless elegance.","colors":["#F5F0EB","#D4AF37"],"sizes":["One Size"],"outfit_type":"accessory"},

    # ── Trouser Collection ─────────────────────────────────────
    {"id":13,"name":"Beige High Waist Wide Leg Trouser","price":999,"category":"trousers","stock":15,"image":"/static/images/products/trouser1.jpg","desc":"Effortlessly chic high-waist wide leg trouser in classic beige. Tailored pleats and a fluid silhouette make this a wardrobe essential for formal and office wear. Pairs beautifully with a tucked-in top or fitted turtleneck.","colors":["#E8D5C0","#2C2C2C","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":14,"name":"Geometric Print Wide Leg Pants","price":1099,"category":"trousers","stock":12,"image":"/static/images/products/trouser2.jpg","desc":"Bold geometric print in white, yellow and black for the maximalist at heart. High-waisted with a relaxed wide leg — street-style ready and effortlessly cool.","colors":["#FFFFFF","#F0C040","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":15,"name":"Olive High Waist Balloon Trouser","price":1199,"category":"trousers","stock":8,"image":"/static/images/products/trouser3.jpg","desc":"Dramatic balloon silhouette in rich olive linen. Gold button detail at the waistband adds a luxe finish. Inspired by vintage Parisian tailoring — refined yet relaxed.","colors":["#556B2F","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":16,"name":"Apricot Corduroy Wide Leg Pants","price":999,"category":"trousers","stock":14,"image":"/static/images/products/trouser4.jpg","desc":"Soft corduroy texture in warm apricot tones. High-rise fit with side pockets and a relaxed wide leg — perfect for casual days with sneakers or boots.","colors":["#D4A574","#C4A882","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":17,"name":"Chocolate Brown Pleated Palazzo","price":1199,"category":"trousers","stock":6,"image":"/static/images/products/trouser5.jpg","desc":"Sculptural pleated palazzo pants in deep chocolate brown. Voluminous and dramatic — a true fashion statement. Wear with an off-shoulder top for an editorial look.","colors":["#3B2314","#5C3D2E","#8B7355"],"sizes":["XS","S","M","L"],"outfit_type":"bottom"},
    {"id":18,"name":"Sage Green Pleated Trousers","price":1099,"category":"trousers","stock":10,"image":"/static/images/products/trouser6.jpg","desc":"Clean sage green with front pleats and a structured straight leg. Street-style perfect — pairs seamlessly with a white button-down or oversized blazer.","colors":["#8FBC8F","#556B2F","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":19,"name":"Dark Brown Wide Leg Formal Trouser","price":1099,"category":"trousers","stock":9,"image":"/static/images/products/trouser7.jpg","desc":"Deep espresso brown pleated trousers with a relaxed wide leg. Italian-inspired tailoring — wear with a linen shirt for effortless European summer style.","colors":["#2C1A0E","#5C3D2E","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":20,"name":"Khaki Wide Leg Tailored Trousers","price":999,"category":"trousers","stock":11,"image":"/static/images/products/trouser8.jpg","desc":"Warm khaki with deep front pleats and a wide tailored leg. Versatile and polished — transitions effortlessly from office to evening with a simple top swap.","colors":["#C4A882","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},
    {"id":21,"name":"Ivory Structured Pleat Front Pants","price":1099,"category":"trousers","stock":13,"image":"/static/images/products/trouser9.jpg","desc":"Crisp ivory with sculptural pleat detailing and a relaxed wide leg. Minimalist and modern — a capsule wardrobe must-have that pairs with everything.","colors":["#F5F0EB","#E8D5C0","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},

    # ── Summer Wear Collection ─────────────────────────────────
    {"id":34,"name":"Chocolate Brown Ribbed Co-ord Set","price":999,"category":"summer","stock":12,
     "image":"/static/images/products/summer1.jpg",
     "desc":"Dreamy yellow midi dress with delicate ruffle shoulder straps and tiered skirt. Perfect for golden hour beach walks and summer evenings. Lightweight and flattering for all body types.",
     "colors":["#F5C518","#F5F0EB","#E8D5C0"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":35,"name":"Tropical Leaf Print Beach Set","price":999,"category":"summer","stock":8,
     "image":"/static/images/products/summer2.jpg",
     "desc":"Romantic ivory floral maxi dress with dramatic puff sleeves and sweetheart neckline. Cottagecore meets beach elegance. Pair with espadrille wedges and a straw hat.",
     "colors":["#F5F0EB","#E8D5C0","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":36,"name":"Olive Green Waffle Co-ord Set","price":899,"category":"summer","stock":10,
     "image":"/static/images/products/summer3.jpg",
     "desc":"Sweet pink gingham midi dress with puff sleeves, ruffle pockets and gathered skirt. Vintage-inspired charm for picnics, garden parties and summer afternoons.",
     "colors":["#FFB6C1","#F5F0EB","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":37,"name":"Lemon Yellow Waffle Co-ord Set","price":899,"category":"summer","stock":9,
     "image":"/static/images/products/summer4.jpg",
     "desc":"Cheerful yellow plaid midi dress with delicate lace trim hem and puff sleeves. Square neckline with ribbon bow detail. A cottagecore dream for sunny days.",
     "colors":["#F5C518","#F5F0EB","#E8D5C0"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":38,"name":"Floral Print Shirt & Shorts Set","price":999,"category":"summer","stock":11,
     "image":"/static/images/products/summer5.jpg",
     "desc":"Breezy white eyelet embroidered mini dress with ruffle hem and tiered silhouette. Bell sleeves and button-down front. Perfect for brunch, beach days or casual summer outings.",
     "colors":["#F5F0EB","#E8D5C0","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":39,"name":"White Eyelet Bell Sleeve Dress","price":1099,"category":"summer","stock":14,
     "image":"/static/images/products/summer6.jpg",
     "desc":"Vibrant floral print co-ord set with short sleeve shirt and matching shorts. Relaxed beach-ready fit. Great for summer holidays, resort wear and poolside lounging.",
     "colors":["#C8503C","#F5C518","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":40,"name":"Yellow Plaid Puff Sleeve Midi Dress","price":999,"category":"summer","stock":15,
     "image":"/static/images/products/summer7.jpg",
     "desc":"Fresh lemon yellow textured shirt and shorts co-ord set. Lightweight waffle fabric with a relaxed fit. Versatile holiday outfit that works from beach to café.",
     "colors":["#F5C518","#F5F0EB","#8FAF88"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":41,"name":"Pink Gingham Puff Sleeve Dress","price":899,"category":"summer","stock":13,
     "image":"/static/images/products/summer8.jpg",
     "desc":"Cool olive green waffle-textured shirt and shorts set. Minimal and effortlessly stylish for summer. Easy to dress up with loafers or down with sandals.",
     "colors":["#556B2F","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":42,"name":"Ivory Floral Puff Sleeve Maxi Dress","price":1199,"category":"summer","stock":10,
     "image":"/static/images/products/summer9.jpg",
     "desc":"Crisp white shirt with sage green tropical leaf print paired with plain sage shorts. Resort-ready Hawaiian style. Lightweight and breathable for hot summer days.",
     "colors":["#8FAF88","#F5F0EB","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":43,"name":"Yellow Ruffle Shoulder Midi Dress","price":999,"category":"summer","stock":8,
     "image":"/static/images/products/summer10.jpg",
     "desc":"Rich chocolate brown ribbed shirt and shorts set. Textured pleated fabric with a relaxed camp collar. Perfect for beach holidays with a minimal editorial edge.",
     "colors":["#3D2B1F","#5C3D2E","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    # ── Unisex Collection ──────────────────────────────────────
    {"id":54,"name":"Chocolate Brown Oversized Hoodie","price":1299,"category":"unisex","stock":10,
     "image":"/static/images/products/unisex1.jpg",
     "desc":"Cosy oversized beige plaid fleece shacket with chest pockets and wooden buttons. Fall and winter essential. Wear open over a turtleneck or belted as a jacket.","colors":["#C4A882","#F5F0EB","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":55,"name":"Olive Polo Sweatshirt with Stripe Collar","price":1199,"category":"unisex","stock":9,
     "image":"/static/images/products/unisex2.jpg",
     "desc":"Chunky grey and blue plaid oversized shacket with gold buttons. Wear open over a ribbed turtleneck for that effortless layered look. Unisex and universally flattering.","colors":["#808080","#87CEEB","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":56,"name":"Brown California Sweatshirt with Collar","price":1099,"category":"unisex","stock":12,
     "image":"/static/images/products/unisex3.jpg",
     "desc":"Bold tropical floral print short sleeve shirt in dark navy. Vintage 90s inspiration with a modern relaxed fit. Tuck it in with high-waist trousers for an editorial look.","colors":["#2C2C2C","#556B2F","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":57,"name":"Green Botanical Print Oversized Shirt","price":1199,"category":"unisex","stock":11,
     "image":"/static/images/products/unisex4.jpg",
     "desc":"Lush green botanical print relaxed shirt with half sleeves and open collar. Artsy and unique — pairs beautifully with camel trousers and a leather belt.","colors":["#228B22","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":58,"name":"Tropical Floral Print Shirt","price":999,"category":"unisex","stock":14,
     "image":"/static/images/products/unisex5.jpg",
     "desc":"Vintage-inspired brown California Est.1776 sweatshirt with a striped shirt collar detail underneath. 2-in-1 layered look without the bulk. Perfect for casual college days.","colors":["#3D2B1F","#F5F0EB","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":59,"name":"Baby Blue Oversized Hoodie","price":1299,"category":"unisex","stock":12,
     "image":"/static/images/products/unisex6.jpg",
     "desc":"Clean olive green polo sweatshirt with contrasting striped collar and cuffs. Minimal and versatile — dress it up or down. Korean street style staple for every wardrobe.","colors":["#556B2F","#F5F0EB","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":60,"name":"Green Floral Print Wool Scarf","price":1199,"category":"unisex","stock":10,
     "image":"/static/images/products/unisex7.jpg",
     "desc":"Premium heavyweight chocolate brown oversized hoodie with small chest logo. Ultra soft fleece interior. The ultimate comfort piece — pair with wide leg trousers or joggers.","colors":["#3D2B1F","#5C3D2E","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":61,"name":"Orange Plaid Jogger Pants","price":999,"category":"unisex","stock":9,
     "image":"/static/images/products/unisex8.jpg",
     "desc":"Dreamy baby blue premium oversized hoodie with small chest logo detail. Cloud-soft and relaxed. Style with grey joggers and sneakers for the perfect off-duty look.","colors":["#87CEEB","#B0C4DE","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    # ── Jacket Collection ──────────────────────────────────────
    {"id":44,"name":"Grey Plaid Oversized Fleece Shacket","price":1199,"category":"jackets","stock":8,
     "image":"/static/images/products/jacket1.jpg",
     "desc":"Stunning reversible crop jacket in olive green with plaid inner lining. Wear it two ways — solid or plaid. Oversized structured shoulders and gold button detail. A collector's piece.","colors":["#556B2F","#87CEEB","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":45,"name":"Beige Plaid Oversized Shacket","price":1099,"category":"jackets","stock":7,
     "image":"/static/images/products/jacket2.jpg",
     "desc":"Luxurious mint blue wool crop jacket with dramatic draped lapels and belted waist. Balloon sleeves add architectural drama. A minimalist statement piece for cooler days.","colors":["#87CEEB","#B0C4DE","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":46,"name":"Camel Contrast Collar Coach Jacket","price":1199,"category":"jackets","stock":6,
     "image":"/static/images/products/jacket3.jpg",
     "desc":"Rich forest green cropped wool jacket with slim leather belt and tie cuffs. Structured yet relaxed. A heritage-inspired piece that works from countryside to city.","colors":["#228B22","#2C2C2C","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":47,"name":"Black & Grey Contrast Zip Jacket","price":899,"category":"jackets","stock":10,
     "image":"/static/images/products/jacket4.jpg",
     "desc":"Cosy beige oversized wool-blend shacket with snap buttons and chest pockets. Korean street style inspiration. Perfect layered over a turtleneck or silk slip dress.","colors":["#C4A882","#E8D5C0","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":48,"name":"Olive Faux Leather Patchwork Jacket","price":1499,"category":"jackets","stock":12,
     "image":"/static/images/products/jacket5.jpg",
     "desc":"Clean ivory zip-up crop jacket with oversized cargo pockets. Minimal and effortlessly cool. A Korean fashion staple that pairs with everything from trousers to skirts.","colors":["#F5F0EB","#E8D5C0","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":49,"name":"Cream & Brown Colour Block Jacket","price":1399,"category":"jackets","stock":9,
     "image":"/static/images/products/jacket6.jpg",
     "desc":"Sharp khaki military-inspired bomber jacket with zip closure and multiple pockets. Lightweight and functional for spring and autumn. Wear over a white tee for instant style.","colors":["#C4A882","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":50,"name":"Khaki Military Bomber Jacket","price":1299,"category":"jackets","stock":8,
     "image":"/static/images/products/jacket7.jpg",
     "desc":"Vintage-inspired cream and chocolate brown colour block jacket with zip front. Retro varsity meets modern minimalism. A head-turning piece for casual outings.","colors":["#F5F0EB","#3D2B1F","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":51,"name":"Ivory Zip Up Cargo Jacket","price":999,"category":"jackets","stock":7,
     "image":"/static/images/products/jacket8.jpg",
     "desc":"Edgy olive green jacket with faux leather sleeves and patchwork detail. Snap button closure and large patch pockets. Street style meets autumn sophistication.","colors":["#556B2F","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":52,"name":"Beige Oversized Wool Shacket","price":1199,"category":"jackets","stock":13,
     "image":"/static/images/products/jacket9.jpg",
     "desc":"Bold black and grey contrast colour block zip-up jacket with ribbed cuffs. Urban street style energy. Great for casual days, gym runs or layering over hoodies.","colors":["#2C2C2C","#808080","#1A1A1A"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":53,"name":"Forest Green Belted Wool Jacket","price":1399,"category":"jackets","stock":11,
     "image":"/static/images/products/jacket10.jpg",
     "desc":"Relaxed camel coach jacket with rich brown contrast collar and snap buttons. Drawstring hem for a customised fit. Retro-inspired and effortlessly wearable.","colors":["#C4A882","#3D2B1F","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},


    {"id":86,"name":"Mint Blue Wool Crop Jacket","price":1499,"category":"jackets","stock":7,
     "image":"/static/images/products/jacket11.jpg",
     "desc":"Luxurious mint blue wool crop jacket with dramatic draped lapels and belted waist. Balloon sleeves add architectural drama. A minimalist statement piece for cooler days.","colors":["#87CEEB","#B0C4DE","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":87,"name":"Olive Reversible Crop Trench Jacket","price":1499,"category":"jackets","stock":6,
     "image":"/static/images/products/jacket12.jpg",
     "desc":"Stunning reversible crop jacket in olive green with plaid inner lining. Wear it two ways — solid or plaid. Oversized structured shoulders and gold button detail. A collector's piece.","colors":["#556B2F","#87CEEB","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    # ── Blazer Collection ──────────────────────────────────────
    {"id":23,"name":"Camel Belted Wrap Blazer","price":1999,"category":"blazers","stock":8,
     "image":"/static/images/products/blazer1.jpg",
     "desc":"Luxurious camel wrap blazer with sleek leather belt detail. Oversized silhouette with dramatic lapels. The ultimate power piece — wear over wide leg trousers for a complete look.","colors":["#C4A882","#2C2C2C","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":24,"name":"Burgundy Long Line Blazer","price":2199,"category":"blazers","stock":6,
     "image":"/static/images/products/blazer2.jpg",
     "desc":"Stunning deep burgundy long-line blazer with matching trouser set. Double-breasted detail and structured shoulders. Sophistication at its finest.","colors":["#722F37","#2C2C2C","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":25,"name":"Ivory Gold Button Blazer","price":1799,"category":"blazers","stock":10,
     "image":"/static/images/products/blazer3.jpg",
     "desc":"Clean ivory single-breasted blazer with elegant gold buttons. Classic notch lapel and structured fit. A timeless wardrobe investment.","colors":["#F5F0EB","#D4AF37","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":26,"name":"Grey Pinstripe Single Button Blazer","price":1699,"category":"blazers","stock":9,
     "image":"/static/images/products/blazer4.jpg",
     "desc":"Sharp grey pinstripe blazer with single gold button closure. Tailored silhouette with flap pockets. Office to evening effortlessly.","colors":["#808080","#2C2C2C","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":27,"name":"Cream Fitted Single Button Blazer","price":1799,"category":"blazers","stock":12,
     "image":"/static/images/products/blazer5.jpg",
     "desc":"Impeccably tailored cream blazer with structured shoulders and single gold button. Clean minimal aesthetic for the modern professional woman.","colors":["#F5F0EB","#C4A882","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":28,"name":"Floral Printed Linen Blazer","price":2199,"category":"blazers","stock":7,
     "image":"/static/images/products/blazer6.jpg",
     "desc":"Breathtaking floral print linen blazer in ivory with bold botanical pattern. Statement piece paired with matching wide-leg trousers. Garden party to gallery opening.","colors":["#F5F0EB","#8FAF88","#C8503C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":29,"name":"Ivory Pinstripe Double Breasted Blazer","price":1999,"category":"blazers","stock":8,
     "image":"/static/images/products/blazer7.jpg",
     "desc":"Oversized ivory double-breasted blazer with navy pinstripes and gold buttons. French Riviera meets London tailoring. Wear as a dress or with matching trousers.","colors":["#F5F0EB","#2C2C2C","#D4AF37"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":30,"name":"Olive Linen Casual Blazer","price":1599,"category":"blazers","stock":11,
     "image":"/static/images/products/blazer8.jpg",
     "desc":"Relaxed olive linen blazer with natural wood buttons. Breathable and lightweight — perfect for spring evenings and casual business meetings.","colors":["#556B2F","#8B7355","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":31,"name":"Sky Blue Double Breasted Suit Blazer","price":2199,"category":"blazers","stock":5,
     "image":"/static/images/products/blazer9.jpg",
     "desc":"Breathtaking sky blue double-breasted summer suit blazer with gold buttons. Lightweight and elegant — made for Mediterranean summers and rooftop events.","colors":["#87CEEB","#F5F0EB","#D4AF37"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":32,"name":"All Black Double Breasted Blazer","price":1999,"category":"blazers","stock":9,
     "image":"/static/images/products/blazer10.jpg",
     "desc":"Powerful all-black double-breasted blazer with peak lapels. Worn over a turtleneck for a dramatic monochrome look. Authority and elegance in equal measure.","colors":["#2C2C2C","#1A1A1A","#808080"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":33,"name":"Chocolate Brown Oversized Blazer","price":1799,"category":"blazers","stock":10,
     "image":"/static/images/products/blazer11.jpg",
     "desc":"Relaxed chocolate brown oversized blazer with wide lapels. Effortlessly cool — wear with matching trousers or wide-leg jeans for a minimal editorial look.","colors":["#3D2B1F","#5C3D2E","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":22,"name":"Olive Linen Wide Leg Trousers","price":1199,"category":"trousers","stock":7,"image":"/static/images/products/trouser10.jpg","desc":"Relaxed linen blend in earthy olive green. Deep pleats and a fluid wide leg for that effortless Mediterranean summer look. Perfect with leather sandals or loafers.","colors":["#556B2F","#8B7355","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"bottom"},

    # ── Tops Collection ────────────────────────────────────────
    {"id":70,"name":"Burgundy Plaid Wide Collar Peplum Top","price":749,"category":"tops","stock":18,"image":"/static/images/products/top1.jpg","desc":"Crisp white cotton top with delicate ruffle trim neckline and flutter sleeves. Light, breezy and effortlessly feminine. Pair with high-waist trousers or a midi skirt.","colors":["#F5F0EB","#E8D5C0","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":71,"name":"Cream Mulberry Recipe Polo Tee","price":599,"category":"tops","stock":14,"image":"/static/images/products/top2.jpg","desc":"Relaxed beige linen top with a front knot detail and wide sleeves. Naturally textured fabric that keeps you cool all day. Tuck it in or let it flow free.","colors":["#C4A882","#E8D5C0","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":72,"name":"Burgundy Heart Print Ringer Tee","price":499,"category":"tops","stock":12,"image":"/static/images/products/top3.jpg","desc":"Romantic ivory top with structured square neckline and dramatic puff sleeves. Cottagecore elegance meets modern minimalism. Perfect with wide-leg trousers or a flowy skirt.","colors":["#F5F0EB","#E8D5C0","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":73,"name":"Pink Striped Sailor Collar Top","price":649,"category":"tops","stock":20,"image":"/static/images/products/top4.jpg","desc":"Essential black ribbed turtleneck in premium stretch cotton. Slim fit with long sleeves. The perfect layering piece — wear under a blazer or alone with wide-leg trousers.","colors":["#2C2C2C","#1A1A1A","#808080"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":74,"name":"Cream Revenules Denim Collar Sweatshirt","price":749,"category":"tops","stock":10,"image":"/static/images/products/top5.jpg","desc":"Cosy camel off-shoulder knit top in a fine rib knit. Relaxed neckline with subtle stretch. Style with tailored trousers or high-waist jeans for effortless autumn dressing.","colors":["#C4A882","#E8D5C0","#8B7355"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":75,"name":"Pink Embroidered Polo Top","price":599,"category":"tops","stock":11,"image":"/static/images/products/top6.jpg","desc":"Elegant sage green wrap-style blouse with a self-tie waist and v-neckline. Floaty woven fabric with a subtle sheen. Office to evening in seconds.","colors":["#8FBC8F","#556B2F","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":76,"name":"Navy Bow Contrast Polo Crop Top","price":549,"category":"tops","stock":15,"image":"/static/images/products/top7.jpg","desc":"Sweet ivory broderie anglaise crop top with delicate eyelet embroidery and scalloped hem. Light as air and beautifully detailed. Pair with a midi skirt or high-waist trousers.","colors":["#F5F0EB","#E8D5C0","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":77,"name":"Khaki Ribbed Contrast Collar Crop Top","price":499,"category":"tops","stock":9,"image":"/static/images/products/top8.jpg","desc":"Warm rust-toned linen button-down shirt with relaxed fit and curved hem. Roll the sleeves for casual ease. A wardrobe staple that transitions beautifully across seasons.","colors":["#C8503C","#8B3A2A","#F5F0EB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":78,"name":"White & Brown Striped Polo Crop Top","price":549,"category":"tops","stock":13,"image":"/static/images/products/top9.jpg","desc":"Romantic white blouse with vertical pintuck detailing and voluminous poet sleeves. Vintage-inspired with a modern minimal sensibility. Tuck into tailored trousers for a polished look.","colors":["#F5F0EB","#E8D5C0","#2C2C2C"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    {"id":79,"name":"Khaki Oversized Crop Tee","price":499,"category":"tops","stock":17,"image":"/static/images/products/top10.jpg","desc":"Classic navy and white Breton stripe top with a wide boatneck. French Riviera heritage in premium cotton jersey. The most versatile top in any wardrobe — pairs with everything.","colors":["#2C2C2C","#F5F0EB","#87CEEB"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},


    {"id":91,"name":"Floral Embroidered Espadrille Flats","price":1099,"category":"shoes","stock":14,
     "image":"/static/images/products/shoe3.jpg",
     "desc":"Handcrafted floral embroidered espadrille Mary Janes with lace-up ties. Jute rope sole and canvas upper. Romantic garden party style meets everyday comfort.","colors":["#C4A882","#FFB6C1","#8FAF88"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},

    {"id":92,"name":"Ivory Daisy Embroidered Clogs","price":1299,"category":"shoes","stock":10,
     "image":"/static/images/products/shoe4.jpg",
     "desc":"Adorable ivory mesh clogs with daisy flower embroidery and elastic back strap. Orthopedic-inspired cushioned sole. The perfect blend of comfort and feminine charm.","colors":["#F5F0EB","#E8D5C0","#C4A882"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},

    {"id":93,"name":"Boho Straw Fringe Slide Sandals","price":799,"category":"shoes","stock":18,
     "image":"/static/images/products/shoe5.jpg",
     "desc":"Handwoven water hyacinth straw slide sandals with crochet fringe and floral bow detail. Lightweight and breathable for summer. A beach holiday essential.","colors":["#C4A882","#FFB6C1","#F5F0EB"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},

    {"id":94,"name":"Yellow Confetti Chunky Sneakers","price":999,"category":"shoes","stock":12,
     "image":"/static/images/products/shoe6.jpg",
     "desc":"Playful yellow and white chunky platform sneakers with bold rope laces and confetti print. Statement footwear with a thick sole for extra height. Streetwear meets kawaii.","colors":["#F5C518","#F5F0EB","#FFB6C1"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},

    {"id":95,"name":"Cream Chain Platform Loafers","price":1499,"category":"shoes","stock":9,
     "image":"/static/images/products/shoe7.jpg",
     "desc":"Patent cream platform loafers with gold chain hardware detail. Block heel with chunky sole. A chic everyday shoe that pairs perfectly with trousers, midi skirts or wide-leg jeans.","colors":["#F5F0EB","#C4A882","#2C2C2C"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},

    {"id":96,"name":"Dark Brown Patent Lace-Up Shoes","price":1299,"category":"shoes","stock":11,
     "image":"/static/images/products/shoe8.jpg",
     "desc":"Glossy dark brown patent leather lace-up Oxford shoes with chunky sole. A versatile classic that works with trousers, skirts and dresses. Timeless dark academia aesthetic.","colors":["#3D2B1F","#2C2C2C","#8B4513"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},

    {"id":97,"name":"Brown Suede Bow Mary Janes","price":1199,"category":"shoes","stock":13,
     "image":"/static/images/products/shoe9.jpg",
     "desc":"Rich chocolate brown suede Mary Jane shoes with sweet bow detail and chunky lug sole. Buckle strap closure. The perfect autumn shoe — pairs beautifully with midi skirts and cosy knits.","colors":["#3D2B1F","#8B4513","#2C2C2C"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},

    {"id":98,"name":"Cream Platform Sneakers with Organza Laces","price":1399,"category":"shoes","stock":10,
     "image":"/static/images/products/shoe10.jpg",
     "desc":"Luxe cream platform sneakers featuring sheer organza and leather ribbon laces. Chunky ridged sole with mocha brown accents. Feminine and editorial — a conversation starter on every street.","colors":["#F5F0EB","#8B7355","#C4A882"],"sizes":["36","37","38","39","40","41"],"outfit_type":"shoes"},


    # ── Ethnic Wear Collection ─────────────────────────────────
    {"id":99,"name":"Burgundy & Ivory Pleated Saree Gown","price":3999,"category":"ethnic","stock":8,
     "image":"/static/images/products/ethnic1.jpg",
     "desc":"Exquisite pre-stitched saree gown in deep burgundy with ivory pleated panel and delicate silver floral embroidery. Full sleeves, elegant drape. Perfect for weddings and festive occasions.","colors":["#6B2737","#F5F0EB","#C0C0C0"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":100,"name":"Olive Green Embroidered Sharara Set","price":4499,"category":"ethnic","stock":6,
     "image":"/static/images/products/ethnic2.jpg",
     "desc":"Stunning olive green heavily embroidered sharara set with matching dupatta. Intricate threadwork and sequin detailing throughout. A showstopper for mehendi, wedding and festive events.","colors":["#556B2F","#8B7355","#D4AF37"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":101,"name":"Plum Gold Bridal Lehenga Choli","price":5999,"category":"ethnic","stock":5,
     "image":"/static/images/products/ethnic3.jpg",
     "desc":"Regal plum silk lehenga choli with sweetheart neckline and heavy zari gold border work. Comes with matching net dupatta. A timeless bridal and reception look for the modern Indian woman.","colors":["#6B2737","#D4AF37","#C0C0C0"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":102,"name":"Ivory Puff Sleeve Floral Skirt Set","price":3499,"category":"ethnic","stock":9,
     "image":"/static/images/products/ethnic4.jpg",
     "desc":"Indo-western ivory puff sleeve top with dramatic floral brocade tiered skirt. A fusion masterpiece for cocktail parties, sangeet and festive gatherings. Comes with a pearl necklace accent.","colors":["#F5F0EB","#C8503C","#FFB6C1"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":103,"name":"Sage Green Mirror Work Anarkali Gown","price":4999,"category":"ethnic","stock":7,
     "image":"/static/images/products/ethnic5.jpg",
     "desc":"Floor-length sage green Anarkali gown with full sleeves and delicate mirror and zardozi work. Scalloped dupatta with tassel border. An ethereal choice for weddings, Eid and festival season.","colors":["#8FAF88","#C0C0C0","#D4AF37"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":104,"name":"Mint Floral Embroidered Jacket Lehenga","price":5499,"category":"ethnic","stock":6,
     "image":"/static/images/products/ethnic6.jpg",
     "desc":"Breathtaking mint green jacket-style lehenga with 3D floral and tropical embroidery. Sheer sleeves with mirror detailing. A couture-inspired piece for sangeet, cocktail or reception events.","colors":["#87CEEB","#8FAF88","#D4AF37"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":105,"name":"Ivory Ethnic wear Men","price":1999,"category":"ethnic","stock":8,
    "image":"/static/images/products/ethnic7.jpg",
    "desc":"Sharp and sophisticated bandhgala suit with a structured collar and slim fit silhouette. A modern take on Indian formal wear — perfect for weddings, receptions and corporate ethnic events.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":106,"name":"White Beaded Elegant Outfit","price":2999,"category":"ethnic","stock":3,
    "image":"/static/images/products/ethnic8.jpg",
    "desc":"Modern indo-western outfit combining a tailored jacket with dhoti-style pants. A fusion masterpiece for sangeet nights, cocktail parties and destination weddings. Bold, stylish and effortlessly elegant.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":107,"name":"Pashmina Shawl","price":999,"category":"ethnic","stock":6,
    "image":"/static/images/products/ethnic9.jpg",
    "desc":"Luxurious Kashmiri Pashmina shawl with delicate hand-embroidered border. Softer than cashmere and warmer than wool. Perfect for weddings, winters and gifting. A true heirloom piece you will treasure forever.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":108,"name":"Pista Green Elegant Suit","price" : 2599,"category":"ethnic","stock":4,
    "image":"/static/images/products/ethnic10.jpg",
    "desc":"Sharp and sophisticated pista green suit with a structured collar and slim fit silhouette. A modern take on Indian formal wear — perfect for weddings, receptions and corporate ethnic events.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":109,"name":"Royal Groom Wear","price":3999,"category":"ethnic","stock":3,
    "image":"/static/images/products/ethnic11.jpg",
    "desc":"Sharp and sophisticated bandhgala suit with a structured collar and slim fit silhouette. A modern take on Indian formal wear — perfect for weddings, receptions and corporate ethnic events.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":110,"name":"Royal Elegant Kurta Set","price":2999,"category":"ethnic","stock":4,
    "image":"/static/images/products/ethnic12.jpg",
    "desc":"Regal sherwani with intricate zardozi embroidery and mandarin collar. Tailored fit with a flowing silhouette. The ultimate choice for grooms, wedding guests and festive occasions. Comes with matching churidar.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":111,"name":"Indian Purple Sherwani Set","price":2499,"category":"ethnic","stock":4,
    "image":"/static/images/products/ethnic13.jpg",
    "desc":"Elegant kurta pajama set in premium cotton fabric. Minimal embroidery at the neckline for a refined look. A timeless choice for weddings, family gatherings and festive celebrations.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":112,"name":"Baby Blue Indian Birder Saree","price":2799,"category":"ethnic","stock":3,
    "image":"/static/images/products/ethnic14.jpg",
    "desc":"Elegant saree with graceful drape. Crafted from premium fabric for weddings, receptions and festive occasions. A timeless piece for the modern Indian woman.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    {"id":113,"name":"Pastel Pink Indo Western Wear","price":3499,"category":"ethnic","stock":4,
    "image":"/static/images/products/ethnic15.jpg",
    "desc":"Statement jacket-style lehenga with 3D floral embroidery and sheer sleeves. A couture-inspired piece for sangeet, cocktail and reception events. Guaranteed to steal the show.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    

    {"id":114,"name":"Golden with Peacock designed Saree","price":2499,"category":"ethnic","stock":4,
    "image":"/static/images/products/ethnic16.jpg",
    "desc":"Elegant Golden Indian bordered saree with intricate Peocock Design and graceful drape. Crafted from premium fabric for weddings, receptions and festive occasions. A timeless piece for the modern Indian woman.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":115,"name":"Indo Western style Lush Green Lehenga","price":3799,"category":"ethnic","stock":3,
    "image":"/static/images/products/ethnic17.jpg",
    "desc":"Fusion indo-western outfit blending traditional embroidery with a modern silhouette. Perfect for cocktail parties, sangeet nights and festive gatherings. Turn heads wherever you go.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},

    {"id":116,"name":"Red and Ivory Sharara Set","price":2499,"category":"ethnic","stock":2,
    "image":"/static/images/products/ethnic18.jpg",
    "desc":"Beautifully embroidered sharara set with matching dupatta. Intricate threadwork and mirror detailing throughout. A showstopper for mehendi, wedding and festive events.","colors":["#6B2737"],"sizes":["XS","S","M","L","XL"],"outfit_type":"top"},
    
    # ── Extra Accessories ──────────────────────────────────────
    {"id":88,"name":"Oval Retro Sunglasses Set","price":599,"category":"accessories","stock":30,
     "image":"/static/images/products/acc10.jpg",
     "desc":"Set of 5 retro oval sunglasses in black, tortoise, amber, brown and white. UV400 protection. Y2K-inspired frames that add instant cool to any summer outfit.","colors":["#2C2C2C","#8B4513","#C4A882","#F5F0EB"],"sizes":["One Size"],"outfit_type":"accessory"},

    {"id":89,"name":"Gold Signet Ring Collection","price":799,"category":"accessories","stock":20,
     "image":"/static/images/products/acc11.jpg",
     "desc":"Curated collection of gold-plated signet rings with mother-of-pearl, star and dome designs. Stainless steel base, tarnish-resistant. Stack them or wear solo for a minimal luxury look.","colors":["#D4AF37","#F5F0EB","#C0C0C0"],"sizes":["One Size"],"outfit_type":"accessory"},

    {"id":90,"name":"Gold Stacked Bracelet Set","price":999,"category":"accessories","stock":15,
     "image":"/static/images/products/acc12.jpg",
     "desc":"Elegant gold-toned stacked bracelet set featuring a crystal bangle, plain cuff, and clover chain bracelet. Perfect for layering. Anti-tarnish coating for long-lasting shine.","colors":["#D4AF37","#C0C0C0"],"sizes":["One Size"],"outfit_type":"accessory"},
    {"id":80,"name":"Linen Baseball Cap","price":599,"category":"accessories","stock":22,"image":"/static/images/products/acc4.jpg","desc":"Statement tortoiseshell acetate sunglasses with oversized square frames and UV400 lenses. The ultimate accessory for instant glamour — pairs with any summer or resort look.","colors":["#8B4513","#2C2C2C","#C4A882"],"sizes":["One Size"],"outfit_type":"accessory"},
    {"id":81,"name":"3pc Steel Chain Bracelet Set","price":799,"category":"accessories","stock":18,"image":"/static/images/products/acc5.jpg","desc":"Handwoven natural straw wide-brim sun hat with a satin ribbon detail. The perfect summer accessory for beach days and outdoor events. Packable and travel-friendly.","colors":["#C4A882","#8B7355","#F5F0EB"],"sizes":["One Size"],"outfit_type":"accessory"},
    {"id":82,"name":"Geneva Square Quartz Watch","price":1499,"category":"accessories","stock":16,"image":"/static/images/products/acc6.jpg","desc":"Delicate multi-strand gold chain necklace in 18k gold-fill. Comes pre-layered for effortless styling. Minimalist luxury that elevates any neckline — from a simple tee to an evening gown.","colors":["#D4AF37","#C0C0C0"],"sizes":["One Size"],"outfit_type":"accessory"},
    {"id":83,"name":"Plum Saffiano Crossbody Bag","price":999,"category":"accessories","stock":20,"image":"/static/images/products/acc7.jpg","desc":"Cosy ribbed knit bucket hat in warm cream. A Korean street style essential for autumn and winter. Pairs beautifully with oversized coats, hoodies and wide-leg trousers.","colors":["#F5F0EB","#E8D5C0","#C4A882","#2C2C2C"],"sizes":["One Size"],"outfit_type":"accessory"},
    {"id":84,"name":"Neutral Satin Scrunchie Set (3pc)","price":299,"category":"accessories","stock":14,"image":"/static/images/products/acc8.jpg","desc":"Slim cognac leather belt with a minimal gold buckle. The finishing touch for blazers, wrap dresses and high-waist trousers. Vegetable-tanned leather that ages with character.","colors":["#8B4513","#2C2C2C","#C4A882"],"sizes":["XS","S","M","L","XL"],"outfit_type":"accessory"},
    {"id":85,"name":"Ivory Pearl Headband Set","price":499,"category":"accessories","stock":12,"image":"/static/images/products/acc9.jpg","desc":"Luxurious pure silk square scarf with an original botanical print in terra and sage. Wear as a neckerchief, headband, bag accessory or wrist wrap. Arrives in a gift-ready box.","colors":["#C8775A","#8FAF88","#F5F0EB"],"sizes":["One Size"],"outfit_type":"accessory"},
]

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        size TEXT,
        color TEXT,
        qty INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        user_email TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        qty INTEGER DEFAULT 1,
        size TEXT,
        status TEXT DEFAULT 'completed',
        ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, product_id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        rating INTEGER,
        category TEXT,
        experience TEXT,
        message TEXT NOT NULL,
        recommend TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0] == 0:
        customers = [
            ('Priya Sharma','priya@gmail.com','priya123'),
            ('Meera Nair','meera@gmail.com','meera123'),
            ('Ananya Iyer','ananya@gmail.com','ananya123'),
            ('Fatima Shaikh','fatima@gmail.com','fatima123'),
            ('Ritu Verma','ritu@gmail.com','ritu123'),
            ('Sneha Pillai','sneha@gmail.com','sneha123'),
            ('Kavya Reddy','kavya@gmail.com','kavya123'),
            ('Pooja Singh','pooja@gmail.com','pooja123'),
            ('Divya Menon','divya@gmail.com','divya123'),
            ('Aisha Khan','aisha@gmail.com','aisha123'),
            ('Nisha Patel','nisha@gmail.com','nisha123'),
            ('Sunita Joshi','sunita@gmail.com','sunita123'),
            ('Rekha Gupta','rekha@gmail.com','rekha123'),
            ('Lakshmi Rao','lakshmi@gmail.com','lakshmi123'),
            ('Deepa Thomas','deepa@gmail.com','deepa123'),
            ('Anu Krishnan','anu@gmail.com','anu123'),
            ('Sanya Malhotra','sanya@gmail.com','sanya123'),
            ('Tara Bose','tara@gmail.com','tara123'),
            ('Riya Chopra','riya@gmail.com','riya123'),
            ('Mahi Jain','mahi@gmail.com','mahi123'),
            ('Zara Siddiqui','zara@gmail.com','zara123'),
            ('Nandini Kumar','nandini@gmail.com','nandini123'),
            ('Pallavi Desai','pallavi@gmail.com','pallavi123'),
            ('Isha Mehta','isha@gmail.com','isha123'),
            ('Kritika Saxena','kritika@gmail.com','kritika123'),
            ('Bhavna Agarwal','bhavna@gmail.com','bhavna123'),
            ('Simran Kaur','simran@gmail.com','simran123'),
            ('Neha Tiwari','neha@gmail.com','neha123'),
            ('Aditi Banerjee','aditi@gmail.com','aditi123'),
            ('Ritika Pandey','ritika@gmail.com','ritika123'),
            ('Swati Mishra','swati@gmail.com','swati123'),
            ('Preeti Dubey','preeti@gmail.com','preeti123'),
            ('Shruti Shukla','shruti@gmail.com','shruti123'),
            ('Ankita Yadav','ankita@gmail.com','ankita123'),
            ('Komal Bajaj','komal@gmail.com','komal123'),
        ]
        products_sample = [
            (1,'Linen Summer Dress','summer',2499),
            (2,'Structured Blazer','jackets',4299),
            (3,'Slip Mule Heels','shoes',3199),
            (4,'Wide Leg Trousers','collections',2799),
            (5,'Gold Cuff Bracelet','accessories',1599),
            (6,'Oversized Trench','jackets',5499),
            (7,'Strappy Sandals','shoes',2699),
            (8,'Silk Cami Top','summer',1999),
            (9,'Leather Tote Bag','accessories',4799),
            (10,'Floral Midi Dress','collections',3399),
            (11,'Knit Cardigan','collections',2499),
            (12,'Pearl Drop Earrings','accessories',1299),
        ]
        sizes = ['XS','S','M','L','XL']
        statuses = ['completed','completed','completed','completed','completed','shipped','pending']
        base = datetime.now()
        for name,email,pw in customers:
            days_ago = random.randint(5,90)
            joined = (base-timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            cur.execute('INSERT INTO users (name,email,password,created_at) VALUES (?,?,?,?)',
                        (name,email,hash_pw(pw),joined))
            uid = cur.lastrowid
            for _ in range(random.randint(2,5)):
                days_ago2 = random.randint(0,89)
                order_date = (base-timedelta(days=days_ago2)).strftime('%Y-%m-%d %H:%M:%S')
                pid = random.choice(products_sample)
                cur.execute('''INSERT INTO orders (user_name,user_email,product_id,product_name,category,price,qty,size,status,ordered_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (name,email,pid[0],pid[1],pid[2],pid[3],
                     random.randint(1,2),random.choice(sizes),
                     random.choice(statuses),order_date))
            for _ in range(random.randint(1,2)):
                cpid = random.choice(products_sample)
                cur.execute('INSERT INTO cart (user_id,product_id,size,color,qty) VALUES (?,?,?,?,?)',
                            (uid,cpid[0],random.choice(sizes),'#C4A882',1))
    con.commit(); con.close()

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def get_db(): return sqlite3.connect(DB)

@app.route('/')
def index():
    return render_template('index.html', trending=PRODUCTS[:4], user=session.get('user'))

@app.route('/collections')
def collections():
    return render_template('collections.html', user=session.get('user'))

@app.route('/products')
def products():
    cat = request.args.get('cat','all')
    filtered = PRODUCTS if cat=='all' else [p for p in PRODUCTS if p['category']==cat]
    return render_template('products.html', products=filtered, active=cat, user=session.get('user'))

@app.route('/item/<int:pid>')
def item(pid):
    product = next((p for p in PRODUCTS if p['id']==pid), None)
    if not product: return redirect(url_for('products'))
    related = [p for p in PRODUCTS if p['category']==product['category'] and p['id']!=pid][:4]
    return render_template('item.html', product=product, related=related, user=session.get('user'))

@app.route('/cart-count')
def cart_count():
    if not session.get('user'): return jsonify({'count':0})
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT COUNT(*) FROM cart WHERE user_id=?',(session['user']['id'],))
    n=cur.fetchone()[0]; con.close()
    return jsonify({'count':n})

@app.route('/cart')
def cart():
    if not session.get('user'): return redirect(url_for('index'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT cart.id,product_id,size,color,qty FROM cart WHERE user_id=?',(session['user']['id'],))
    rows=cur.fetchall(); con.close()
    items=[]
    for r in rows:
        p=next((x for x in PRODUCTS if x['id']==r[1]),None)
        if p: items.append({'cart_id':r[0],'product':p,'size':r[2],'color':r[3],'qty':r[4]})
    total=sum(i['product']['price']*i['qty'] for i in items)
    return render_template('cart.html',items=items,total=total,user=session.get('user'))

@app.route('/add-to-cart',methods=['POST'])
def add_to_cart():
    if not session.get('user'): return jsonify({'error':'login'}),401
    data=request.json
    con=get_db(); cur=con.cursor()
    cur.execute('INSERT INTO cart (user_id,product_id,size,color,qty) VALUES (?,?,?,?,1)',
                (session['user']['id'],data['product_id'],data.get('size','M'),data.get('color','#C4A882')))
    con.commit(); con.close()
    return jsonify({'success':True})

@app.route('/remove-from-cart/<int:cid>',methods=['POST'])
def remove_from_cart(cid):
    con=get_db(); cur=con.cursor()
    cur.execute('DELETE FROM cart WHERE id=? AND user_id=?',(cid,session['user']['id']))
    con.commit(); con.close()
    return redirect(url_for('cart'))

@app.route('/wishlist')
def wishlist():
    if not session.get('user'): return redirect(url_for('index'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT product_id FROM wishlist WHERE user_id=?',(session['user']['id'],))
    pids=[r[0] for r in cur.fetchall()]; con.close()
    items=[p for p in PRODUCTS if p['id'] in pids]
    return render_template('wishlist.html',items=items,user=session.get('user'))

@app.route('/toggle-wishlist',methods=['POST'])
def toggle_wishlist():
    if not session.get('user'): return jsonify({'error':'login'}),401
    pid=request.json.get('product_id')
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id FROM wishlist WHERE user_id=? AND product_id=?',(session['user']['id'],pid))
    exists=cur.fetchone()
    if exists:
        cur.execute('DELETE FROM wishlist WHERE user_id=? AND product_id=?',(session['user']['id'],pid))
        con.commit(); con.close()
        return jsonify({'status':'removed','msg':'Removed from wishlist'})
    else:
        cur.execute('INSERT INTO wishlist (user_id,product_id) VALUES (?,?)',(session['user']['id'],pid))
        con.commit(); con.close()
        return jsonify({'status':'added','msg':'Added to wishlist ♡'})

@app.route('/orders')
def order_history():
    if not session.get('user'): return redirect(url_for('index'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id,product_name,category,price,qty,size,status,ordered_at FROM orders WHERE user_email=? ORDER BY ordered_at DESC',
                (session['user']['email'],))
    rows=cur.fetchall(); con.close()
    orders=[]
    for r in rows:
        pid_match=next((p for p in PRODUCTS if p['name']==r[1]),None)
        # Check if order can be cancelled (within 24 hours and not cancelled/shipped)
        can_cancel = False
        if r[6] in ['pending', 'completed'] and r[7]:
            try:
                order_time = datetime.strptime(r[7], '%Y-%m-%d %H:%M:%S')
                time_diff = datetime.now() - order_time
                can_cancel = time_diff.total_seconds() < 86400  # 24 hours in seconds
            except:
                pass
        orders.append({'id':r[0],'product_name':r[1],'category':r[2],'price':r[3],
                       'qty':r[4],'size':r[5],'status':r[6],'date':r[7][:10] if r[7] else '',
                       'image':pid_match['image'] if pid_match else '', 'can_cancel':can_cancel})
    return render_template('orders.html',orders=orders,user=session.get('user'))

@app.route('/cancel-order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if not session.get('user'): return jsonify({'success':False,'message':'Please login first'})
    
    con=get_db(); cur=con.cursor()
    # Get order details
    cur.execute('SELECT status,ordered_at,user_email FROM orders WHERE id=? AND user_email=?',
                (order_id, session['user']['email']))
    order = cur.fetchone()
    
    if not order:
        con.close()
        return jsonify({'success':False,'message':'Order not found'})
    
    status, ordered_at, user_email = order
    
    # Check if order can be cancelled
    if status not in ['pending', 'completed']:
        con.close()
        return jsonify({'success':False,'message':'Order cannot be cancelled'})
    
    if not ordered_at:
        con.close()
        return jsonify({'success':False,'message':'Invalid order time'})
    
    try:
        order_time = datetime.strptime(ordered_at, '%Y-%m-%d %H:%M:%S')
        time_diff = datetime.now() - order_time
        if time_diff.total_seconds() >= 86400:  # 24 hours
            con.close()
            return jsonify({'success':False,'message':'Order can only be cancelled within 24 hours'})
    except:
        con.close()
        return jsonify({'success':False,'message':'Invalid order time'})
    
    # Update order status to cancelled
    cur.execute('UPDATE orders SET status=? WHERE id=?', ('cancelled', order_id))
    con.commit()
    con.close()
    
    return jsonify({
        'success':True,
        'message':'Order cancelled successfully! Your payment will be refunded within 3-5 business days. Thank you for shopping with AFZO Clothing!'
    })

@app.route('/outfit-builder')
def outfit_builder():
    if not session.get('user'): return redirect(url_for('index'))
    tops=[p for p in PRODUCTS if p['outfit_type']=='top']
    bottoms=[p for p in PRODUCTS if p['outfit_type']=='bottom']
    shoes=[p for p in PRODUCTS if p['outfit_type']=='shoes']
    accessories=[p for p in PRODUCTS if p['outfit_type']=='accessory']
    return render_template('outfit_builder.html',tops=tops,bottoms=bottoms,
                           shoes=shoes,accessories=accessories,user=session.get('user'))

@app.route('/checkout')
def checkout():
    if not session.get('user'): return redirect(url_for('index'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT cart.id,product_id,size,color,qty FROM cart WHERE user_id=?',(session['user']['id'],))
    rows=cur.fetchall(); con.close()
    items=[]
    for r in rows:
        p=next((x for x in PRODUCTS if x['id']==r[1]),None)
        if p: items.append({'cart_id':r[0],'product':p,'size':r[2],'color':r[3],'qty':r[4]})
    if not items: return redirect(url_for('cart'))
    total=sum(i['product']['price']*i['qty'] for i in items)
    discount = total * 0.2 if session.get('discount_applied') else 0
    final_total = total - discount
    return render_template('checkout.html',items=items,total=total,discount=discount,final_total=final_total,user=session.get('user'))

@app.route('/apply-discount',methods=['POST'])
def apply_discount():
    if not session.get('user'): return jsonify({'error':'login'}),401
    code=request.json.get('code','').upper()
    if code==DISCOUNT_CODE:
        session['discount_applied']=True
        con=get_db(); cur=con.cursor()
        cur.execute('SELECT product_id,qty FROM cart WHERE user_id=?',(session['user']['id'],))
        cart_items=cur.fetchall(); con.close()
        total = sum(next((x['price'] for x in PRODUCTS if x['id']==pid), 0) * qty for pid,qty in cart_items)
        discount_amount = int(total * 0.2)
        return jsonify({'success':True,'discount':20,'discount_amount':discount_amount})
    return jsonify({'error':'Invalid discount code'}),400

@app.route('/place-order',methods=['POST'])
def place_order():
    if not session.get('user'): return jsonify({'error':'login'}),401
    data=request.json
    payment_method = data.get('payment_method', 'cod')
    
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT cart.id,product_id,size,color,qty FROM cart WHERE user_id=?',(session['user']['id'],))
    cart_items=cur.fetchall()
    if not cart_items: return jsonify({'error':'Cart is empty'}),400
    
    discount_applied = session.get('discount_applied', False)
    for cid,pid,size,color,qty in cart_items:
        p=next((x for x in PRODUCTS if x['id']==pid),None)
        if p:
            price = p['price'] * 0.8 if discount_applied else p['price']
            status = 'completed' if payment_method in ['card','upi'] else 'pending'
            cur.execute('''INSERT INTO orders (user_name,user_email,product_id,product_name,category,price,qty,size,status)
                VALUES (?,?,?,?,?,?,?,?,?)''',
                (session['user']['name'],session['user']['email'],pid,p['name'],p['category'],price,qty,size,status))
            cur.execute('DELETE FROM cart WHERE id=?',(cid,))
    con.commit(); con.close()
    session.pop('discount_applied',None)
    return jsonify({'success':True,'message':'Order placed successfully!'})

@app.route('/offers')
def offers():
    return render_template('offers.html',user=session.get('user'))

@app.route('/subscribe',methods=['POST'])
def subscribe():
    return jsonify({'success':True})

@app.route('/signup',methods=['POST'])
def signup():
    data=request.json
    con=get_db(); cur=con.cursor()
    try:
        cur.execute('INSERT INTO users (name,email,password) VALUES (?,?,?)',
                    (data['name'],data['email'],hash_pw(data['password'])))
        con.commit()
        uid=cur.lastrowid
        session['user']={'id':uid,'name':data['name'],'email':data['email']}
        return jsonify({'success':True,'name':data['name']})
    except sqlite3.IntegrityError:
        return jsonify({'error':'Email already registered'}),400
    finally: con.close()

@app.route('/login',methods=['POST'])
def login():
    data=request.json
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id,name,email FROM users WHERE email=? AND password=?',
                (data['email'],hash_pw(data['password'])))
    user=cur.fetchone(); con.close()
    if user:
        session['user']={'id':user[0],'name':user[1],'email':user[2]}
        return jsonify({'success':True,'name':user[1]})
    return jsonify({'error':'Invalid email or password'}),401

@app.route('/feedback', methods=['GET','POST'])
def feedback():
    success = False
    if request.method == 'POST':
        data = request.form
        con = get_db()
        cur = con.cursor()
        cur.execute('''INSERT INTO feedback (name, email, rating, category, experience, message, recommend)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (data['name'], data['email'], int(data.get('rating', 0)), data.get('category', ''),
                     data.get('experience', ''), data['message'], data.get('recommend', '')))
        con.commit()
        con.close()
        success = True
    return render_template('feedback.html', user=session.get('user'), success=success)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── ADMIN ──────────────────────────────────────────────────────
def admin_required(): return session.get('admin')==True

@app.route('/admin')
def admin_login_page():
    if admin_required(): return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/login',methods=['POST'])
def admin_login():
    data=request.json
    if data['email']==ADMIN_EMAIL and data['password']==ADMIN_PASSWORD:
        session['admin']=True
        return jsonify({'success':True})
    return jsonify({'error':'Invalid admin credentials'}),401

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin',None)
    return redirect(url_for('admin_login_page'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not admin_required(): return redirect(url_for('admin_login_page'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT COUNT(*) FROM orders WHERE status="completed"')
    total_orders=cur.fetchone()[0]
    cur.execute('SELECT SUM(price*qty) FROM orders WHERE status="completed"')
    total_revenue=cur.fetchone()[0] or 0
    cur.execute('SELECT COUNT(*) FROM users')
    total_users=cur.fetchone()[0]
    cur.execute('SELECT COUNT(DISTINCT user_email) FROM orders')
    total_customers=cur.fetchone()[0]
    base=datetime.now()
    revenue_7days=[]; labels_7days=[]
    for i in range(6,-1,-1):
        d=(base-timedelta(days=i)).strftime('%Y-%m-%d')
        cur.execute('SELECT COALESCE(SUM(price*qty),0) FROM orders WHERE DATE(ordered_at)=? AND status="completed"',(d,))
        revenue_7days.append(round(cur.fetchone()[0],2))
        labels_7days.append((base-timedelta(days=i)).strftime('%d %b'))
    cur.execute('SELECT category,COUNT(*),SUM(price*qty) FROM orders GROUP BY category ORDER BY COUNT(*) DESC')
    cat_rows=cur.fetchall()
    cat_labels=[r[0].title() for r in cat_rows]
    cat_orders=[r[1] for r in cat_rows]
    cat_revenue=[round(r[2] or 0, 2) for r in cat_rows]
    cur.execute('SELECT product_name,COUNT(*) as cnt,SUM(price*qty) FROM orders GROUP BY product_name ORDER BY cnt DESC LIMIT 5')
    prod_rows=cur.fetchall()
    prod_labels=[r[0] for r in prod_rows]
    prod_counts=[r[1] for r in prod_rows]
    prod_revenue=[round(r[2] or 0, 2) for r in prod_rows]
    cur.execute('SELECT id,user_name,user_email,product_name,category,price,qty,size,status,ordered_at FROM orders ORDER BY ordered_at DESC LIMIT 15')
    recent_orders=cur.fetchall()
    cur.execute('SELECT id,name,email,created_at FROM users ORDER BY created_at DESC')
    all_users=cur.fetchall()
    cur.execute('SELECT user_name,user_email,COUNT(*) as orders,SUM(price*qty) as spent FROM orders WHERE status="completed" GROUP BY user_email ORDER BY spent DESC LIMIT 5')
    leaderboard_raw=cur.fetchall()
    leaderboard=[]
    for name,email,orders,spent in leaderboard_raw:
        cur.execute('SELECT id FROM users WHERE email=?',(email,))
        uid_result=cur.fetchone()
        uid=uid_result[0] if uid_result else None
        leaderboard.append((name,email,orders,spent or 0,uid))
    cur.execute('SELECT id,name,email,rating,category,experience,message,recommend,submitted_at FROM feedback ORDER BY submitted_at DESC LIMIT 15')
    recent_feedback=cur.fetchall()
    low_stock=[p for p in PRODUCTS if p['stock']<6]
    con.close()
    return render_template('admin_dashboard.html',
        total_orders=total_orders,total_revenue=round(total_revenue,2),
        total_users=total_users,total_customers=total_customers,
        revenue_7days=revenue_7days,labels_7days=labels_7days,
        cat_labels=cat_labels,cat_orders=cat_orders,cat_revenue=cat_revenue,
        prod_labels=prod_labels,prod_counts=prod_counts,prod_revenue=prod_revenue,
        recent_orders=recent_orders,all_users=all_users,
        leaderboard=leaderboard,recent_feedback=recent_feedback,low_stock=low_stock)

@app.route('/admin/feedback/<int:fid>')
def admin_feedback_detail(fid):
    if not admin_required(): return redirect(url_for('admin_login_page'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id,name,email,rating,category,experience,message,recommend,submitted_at FROM feedback WHERE id=?',(fid,))
    feedback=cur.fetchone(); con.close()
    if not feedback: return redirect(url_for('admin_dashboard'))
    return render_template('admin_feedback_detail.html', feedback=feedback)

@app.route('/admin/user/<int:uid>')
def admin_user_detail(uid):
    if not admin_required(): return redirect(url_for('admin_login_page'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id,name,email,created_at FROM users WHERE id=?',(uid,))
    user=cur.fetchone()
    if not user: return redirect(url_for('admin_dashboard'))
    cur.execute('SELECT id,product_name,category,price,qty,size,status,ordered_at FROM orders WHERE user_email=? ORDER BY ordered_at DESC',(user[2],))
    orders=cur.fetchall()
    cur.execute('SELECT product_id FROM wishlist WHERE user_id=?',(uid,))
    wishlist_ids=[r[0] for r in cur.fetchall()]
    wishlist=[p for p in PRODUCTS if p['id'] in wishlist_ids]
    cur.execute('SELECT cart.product_id,cart.size,cart.color,cart.qty FROM cart WHERE cart.user_id=?',(uid,))
    cart_rows=cur.fetchall()
    cart_items=[]
    for r in cart_rows:
        p=next((x for x in PRODUCTS if x['id']==r[0]),None)
        if p: cart_items.append({'product':p,'size':r[1],'color':r[2],'qty':r[3]})
    con.close()
    return render_template('admin_user_detail.html', user=user, orders=orders, wishlist=wishlist, cart_items=cart_items)

@app.route('/admin/order/<int:oid>')
def admin_order_detail(oid):
    if not admin_required(): return redirect(url_for('admin_login_page'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id,user_name,user_email,product_id,product_name,price,qty,size,status,ordered_at FROM orders WHERE id=?',(oid,))
    order=cur.fetchone(); con.close()
    if not order: return redirect(url_for('admin_dashboard'))
    product=next((p for p in PRODUCTS if p['id']==order[3]),None)
    return render_template('admin_order_detail.html', order=order, product=product)

@app.route('/admin/all-orders')
def admin_all_orders():
    if not admin_required(): return redirect(url_for('admin_login_page'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id,user_name,user_email,product_name,price,qty,size,status,ordered_at FROM orders ORDER BY ordered_at DESC')
    all_orders=cur.fetchall(); con.close()
    return render_template('admin_all_orders.html', all_orders=all_orders)

@app.route('/admin/all-users')
def admin_all_users():
    if not admin_required(): return redirect(url_for('admin_login_page'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT id,name,email,created_at FROM users ORDER BY created_at DESC')
    all_users=cur.fetchall(); con.close()
    return render_template('admin_all_users.html', all_users=all_users)

@app.route('/admin/all-customers')
def admin_all_customers():
    if not admin_required(): return redirect(url_for('admin_login_page'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT DISTINCT user_name,user_email,COUNT(*) as orders,SUM(price*qty) as spent FROM orders GROUP BY user_email ORDER BY spent DESC')
    customers=cur.fetchall()
    customer_list=[]
    for name,email,orders,spent in customers:
        cur.execute('SELECT id FROM users WHERE email=?',(email,))
        uid_result=cur.fetchone()
        uid=uid_result[0] if uid_result else None
        customer_list.append((name,email,orders,spent,uid))
    con.close()
    return render_template('admin_all_customers.html', customers=customer_list)

@app.route('/admin/category/<category>')
def admin_category_detail(category):
    if not admin_required(): return redirect(url_for('admin_login_page'))
    category_lower = category.lower()
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT product_name,COUNT(*) as cnt,SUM(price*qty) as revenue FROM orders WHERE LOWER(category)=? GROUP BY product_name ORDER BY cnt DESC',(category_lower,))
    products=cur.fetchall()
    cur.execute('SELECT COUNT(*),SUM(price*qty) FROM orders WHERE LOWER(category)=?',(category_lower,))
    cat_stats=cur.fetchone()
    con.close()
    top_product_name=products[0][0] if products else None
    top_product=next((p for p in PRODUCTS if p['name']==top_product_name),None)
    return render_template('admin_category_detail.html', category=category, top_product=top_product, 
                          product_list=products, cat_total_orders=cat_stats[0], cat_revenue=cat_stats[1] or 0)

@app.route('/admin/product-detail/<product_name>')
def admin_product_detail_by_name(product_name):
    if not admin_required(): return redirect(url_for('admin_login_page'))
    product=next((p for p in PRODUCTS if p['name']==product_name),None)
    if not product: return redirect(url_for('admin_dashboard'))
    con=get_db(); cur=con.cursor()
    cur.execute('SELECT COUNT(*),SUM(price*qty) FROM orders WHERE product_name=?',(product_name,))
    stats=cur.fetchone()
    cur.execute('SELECT id,user_name,user_email,qty,size,status,ordered_at FROM orders WHERE product_name=? ORDER BY ordered_at DESC LIMIT 10',(product_name,))
    sales=cur.fetchall()
    con.close()
    return render_template('admin_product_detail.html', product=product, total_sold=stats[0], total_revenue=stats[1] or 0, sales=sales)

if __name__=='__main__':
    init_db()
    app.run(debug=True,host='0.0.0.0',port=5000)
