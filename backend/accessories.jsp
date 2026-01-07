<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopping Website</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }

        header {
            background-color: #2e3c4e;
            color: white;
            padding: 1em;
            text-align: center;
        }

        #products {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            padding: 20px;
        }

        .product {
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 20px;
            padding: 30px;
            width: 400px;
            background-color: white;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 10);
        }

        button {
            background-color: #f06292;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }

        button:hover {
            background-color: #ec407a;
        }
    </style>
</head>
<body>
    <header>
        <h1>ACCESSORIES</h1>
    </header>
    
    <div id="products">

        <div class="product">
            <h2>Product 1</h2>
            <p>Description of Product 1.</p>
            <a href="models/Accessories/p1.html"><img height="230" src="models/Accessories/images/ap1.png" alt="shirt"></a>
            <p>Cost: 1000</p>
            <form method="post" action="addToCart.jsp">
                <input type="hidden" name="product_name" value="Product 1">
                <input type="hidden" name="product_description" value="Description of Product 1">
                <input type="hidden" name="product_image" value="models/Accessories/images/ap1.png">
                <input type="hidden" name="product_cost" value="1000">
                <input type="hidden" name="quantity" value="1">
                <button type="submit">Add to Cart</button>
            </form>
        </div>

        <div class="product">
            <h2>Product 2</h2>
            <p>Description of Product 2.</p>
            <a href="models/Accessories/p2.html"><img height="230" src="models/Accessories/images/ap2.png" alt="shirt"></a>
            <p>Cost: 1000</p>
            <form method="post" action="addToCart.jsp">
                <input type="hidden" name="product_name" value="Product 2">
                <input type="hidden" name="product_description" value="Description of Product 2">
                <input type="hidden" name="product_image" value="models/Accessories/images/ap2.png">
                <input type="hidden" name="product_cost" value="1000">
                <input type="hidden" name="quantity" value="1">
                <button type="submit">Add to Cart</button>
            </form>
        </div>

        <div class="product">
            <h2>Product 3</h2>
            <p>Description of Product 3.</p>
            <a href="models/Accessories/p3.html"><img height="230" src="models/Accessories/images/ap3.png" alt="shirt"></a>
            <p>Cost: 1000</p>
            <form method="post" action="addToCart.jsp">
                <input type="hidden" name="product_name" value="Product 3">
                <input type="hidden" name="product_description" value="Description of Product 3">
                <input type="hidden" name="product_image" value="models/Accessories/images/ap3.png">
                <input type="hidden" name="product_cost" value="1000">
                <input type="hidden" name="quantity" value="1">
                <button type="submit">Add to Cart</button>
            </form>
        </div>

     

        <div class="product">
            <h2>Product 5</h2>
            <p>Description of Product 5.</p>
            <a href="models/Accessories/p5.html"><img height="230" src="models/Accessories/images/ap4.png" alt="shirt"></a>
            <p>Cost: 1000</p>
            <form method="post" action="addToCart.jsp">
                <input type="hidden" name="product_name" value="Product 5">
                <input type="hidden" name="product_description" value="Description of Product 5">
                <input type="hidden" name="product_image" value="models/Accessories/images/ap4.png">
                <input type="hidden" name="product_cost" value="1000">
                <input type="hidden" name="quantity" value="1">
                <button type="submit">Add to Cart</button>
            </form>
        </div>

        <div class="product">
            <h2>Product 6</h2>
            <p>Description of Product 6.</p>
            <a href="models/Accessories/p6.html"><img height="230" src="models/Accessories/images/ap5.png" alt="shirt"></a>
            <p>Cost: 1000</p>
            <form method="post" action="addToCart.jsp">
                <input type="hidden" name="product_name" value="Product 6">
                <input type="hidden" name="product_description" value="Description of Product 6">
                <input type="hidden" name="product_image" value="models/Accessories/images/ap5.png">
                <input type="hidden" name="product_cost" value="1000">
                <input type="hidden" name="quantity" value="1">
                <button type="submit">Add to Cart</button>
            </form>
        </div>

        <div class="product">
            <h2>Product 7</h2>
            <p>Description of Product 7.</p>
            <a href="models/Accessories/p7.html"><img height="230" src="models/Accessories/images/ap6.png" alt="shirt"></a>
            <p>Cost: 1000</p>
            <form method="post" action="addToCart.jsp">
                <input type="hidden" name="product_name" value="Product 7">
                <input type="hidden" name="product_description" value="Description of Product 7">
                <input type="hidden" name="product_image" value="models/Accessories/images/ap6.png">
                <input type="hidden" name="product_cost" value="1000">
                <input type="hidden" name="quantity" value="1">
                <button type="submit">Add to Cart</button>
            </form>
        </div>

        <div class="product">
            <h2>Product 8</h2>
            <p>Description of Product 8.</p>
            <a href="models/Accessories/p8.html"><img height="230" src="models/Accessories/images/ap7.png" alt="shirt"></a>
            <p>Cost: 1000</p>
            <form method="post" action="addToCart.jsp">
                <input type="hidden" name="product_name" value="Product 8">
                <input type="hidden" name="product_description" value="Description of Product 8">
                <input type="hidden" name="product_image" value="models/Accessories/images/ap7.png">
                <input type="hidden" name="product_cost" value="1000">
                <input type="hidden" name="quantity" value="1">
                <button type="submit">Add to Cart</button>
            </form>
        </div>

       

        <!-- Add more products as needed -->
    </div>
    <footer>
        <p>&copy; Online Website</p>
    </footer>
</body>
</html>
