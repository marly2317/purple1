import sqlite3

def init_database():
    try:
        conn = sqlite3.connect('shopping_assistant.sqlite')
        cursor = conn.cursor()
        
        # Удаление таблиц, если они существуют
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS cart")
        
        # Создание таблицы products с новым столбцом gender
        cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL,
            discountPercentage REAL DEFAULT 0.0,
            rating REAL DEFAULT 0.0,
            stock INTEGER DEFAULT 0,
            brand TEXT,
            category TEXT,
            thumbnail TEXT,
            gender TEXT  -- Новый столбец для указания пола (male, female, unisex)
        )
        ''')

        # Создание таблицы cart
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            user_id TEXT,
            product_id INTEGER,
            quantity INTEGER,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        ''')

        # Добавление данных с учетом нового столбца gender
        sample_products = [
            # Одежда
            ('Evening Dress', 'Elegant evening dress with deep neckline', 250.00, 15.0, 4.8, 20, 'Gucci', 'Clothing', 'evening_dress.jpg', 'female'),
            ('Business Suit', 'Tailored business suit for men', 350.00, 10.0, 4.6, 30, 'Armani', 'Clothing', 'business_suit.jpg', 'male'),
            ('Casual T-Shirt', 'Comfortable cotton t-shirt', 25.00, 5.0, 4.2, 100, 'Nike', 'Clothing', 'casual_tshirt.jpg', 'unisex'),
            ('Denim Jeans', 'Slim-fit denim jeans', 60.00, 10.0, 4.3, 80, 'Levi\'s', 'Clothing', 'denim_jeans.jpg', 'unisex'),
            ('Wool Coat', 'Warm wool coat for winter', 200.00, 15.0, 4.5, 25, 'Burberry', 'Clothing', 'wool_coat.jpg', 'female'),
            ('Cocktail Dress', 'Chic cocktail dress for parties', 180.00, 10.0, 4.7, 20, 'Versace', 'Clothing', 'cocktail_dress.jpg', 'female'),
            ('Sports Jacket', 'Waterproof sports jacket', 90.00, 10.0, 4.4, 50, 'The North Face', 'Clothing', 'sports_jacket.jpg', 'unisex'),
            ('Blazer', 'Structured blazer for women', 120.00, 10.0, 4.5, 35, 'Zara', 'Clothing', 'blazer.jpg', 'female'),
            ('Knit Sweater', 'Cozy knit sweater', 45.00, 5.0, 4.3, 60, 'H&M', 'Clothing', 'knit_sweater.jpg', 'unisex'),
            ('Summer Skirt', 'Flowy summer skirt', 35.00, 5.0, 4.2, 70, 'Mango', 'Clothing', 'summer_skirt.jpg', 'female'),

            # Обувь
            ('Running Shoes', 'Lightweight running shoes with cushioning', 80.00, 10.0, 4.5, 60, 'Adidas', 'Footwear', 'running_shoes.jpg', 'unisex'),
            ('Leather Boots', 'Stylish leather boots for winter', 120.00, 15.0, 4.7, 40, 'Timberland', 'Footwear', 'leather_boots.jpg', 'male'),
            ('High Heels', 'Elegant high heels for formal events', 90.00, 10.0, 4.4, 50, 'Jimmy Choo', 'Footwear', 'high_heels.jpg', 'female'),
            ('Casual Sneakers', 'Versatile white sneakers', 55.00, 5.0, 4.3, 90, 'Converse', 'Footwear', 'casual_sneakers.jpg', 'unisex'),
            ('Sandals', 'Comfortable flat sandals', 40.00, 5.0, 4.2, 80, 'Birkenstock', 'Footwear', 'sandals.jpg', 'female'),
            ('Ankle Boots', 'Chic ankle boots with low heel', 100.00, 10.0, 4.6, 45, 'Clarks', 'Footwear', 'ankle_boots.jpg', 'female'),
            ('Loafers', 'Classic leather loafers', 85.00, 10.0, 4.4, 50, 'Tod\'s', 'Footwear', 'loafers.jpg', 'male'),

            # Аксессуары
            ('Leather Handbag', 'Classic leather handbag', 150.00, 10.0, 4.6, 30, 'Louis Vuitton', 'Accessories', 'leather_handbag.jpg', 'female'),
            ('Silk Scarf', 'Luxurious silk scarf', 70.00, 10.0, 4.3, 40, 'Hermes', 'Accessories', 'silk_scarf.jpg', 'female'),
            ('Sunglasses', 'Stylish sunglasses with UV protection', 50.00, 10.0, 4.2, 100, 'Ray-Ban', 'Accessories', 'sunglasses.jpg', 'unisex'),
            ('Leather Belt', 'Classic leather belt', 40.00, 10.0, 4.3, 70, 'Calvin Klein', 'Accessories', 'leather_belt.jpg', 'male'),
            ('Wristwatch', 'Elegant wristwatch with leather strap', 120.00, 10.0, 4.6, 30, 'Rolex', 'Accessories', 'wristwatch.jpg', 'male'),
            ('Statement Necklace', 'Bold statement necklace', 60.00, 10.0, 4.4, 25, 'Swarovski', 'Accessories', 'statement_necklace.jpg', 'female'),
            ('Tote Bag', 'Spacious tote bag', 80.00, 10.0, 4.5, 40, 'Michael Kors', 'Accessories', 'tote_bag.jpg', 'female'),
            ('Fedora Hat', 'Stylish fedora hat', 45.00, 5.0, 4.3, 50, 'Brixton', 'Accessories', 'fedora_hat.jpg', 'unisex'),

            # Деловая одежда
            ('Classic White Shirt', 'Crisp white shirt for formal occasions', 50.00, 5.0, 4.5, 100, 'Hugo Boss', 'Business Clothing', 'white_shirt.jpg', 'male'),
            ('Tailored Trousers', 'Slim-fit tailored trousers', 80.00, 10.0, 4.6, 70, 'Zegna', 'Business Clothing', 'tailored_trousers.jpg', 'male'),
            ('Pencil Skirt', 'Formal pencil skirt for women', 70.00, 10.0, 4.4, 60, 'Calvin Klein', 'Business Clothing', 'pencil_skirt.jpg', 'female'),
            ('Double-Breasted Blazer', 'Elegant double-breasted blazer', 150.00, 15.0, 4.7, 40, 'Tom Ford', 'Business Clothing', 'double_breasted_blazer.jpg', 'male'),
            ('Dress Shirt', 'Formal dress shirt with French cuffs', 60.00, 5.0, 4.5, 90, 'Brooks Brothers', 'Business Clothing', 'dress_shirt.jpg', 'male'),
            ('Wool Trousers', 'Warm wool trousers for winter', 100.00, 10.0, 4.6, 50, 'Ralph Lauren', 'Business Clothing', 'wool_trousers.jpg', 'male'),
            ('Silk Blouse', 'Elegant silk blouse for women', 90.00, 10.0, 4.5, 55, 'Theory', 'Business Clothing', 'silk_blouse.jpg', 'female'),
            ('Vest Waistcoat', 'Formal vest waistcoat for men', 75.00, 10.0, 4.4, 45, 'Ted Baker', 'Business Clothing', 'vest_waistcoat.jpg', 'male'),
            ('A-Line Skirt', 'Classic A-line skirt for office wear', 65.00, 10.0, 4.3, 60, 'Banana Republic', 'Business Clothing', 'a_line_skirt.jpg', 'female'),
            ('Cashmere Sweater', 'Luxurious cashmere sweater', 120.00, 15.0, 4.7, 35, 'Brunello Cucinelli', 'Business Clothing', 'cashmere_sweater.jpg', 'unisex'),
        ]
        
        # Проверка, пустая ли таблица
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany('''
                INSERT INTO products (title, description, price, discountPercentage, rating, stock, brand, category, thumbnail, gender) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            ''', sample_products)
        
        conn.commit()
        conn.close()
        print("База данных успешно инициализирована!")
        return True
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        return False

if __name__ == '__main__':
    init_database()