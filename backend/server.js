const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 4000;
const JWT_SECRET = 'your_jwt_secret_key'; // Use a strong secret key

app.use(cors());
app.use(bodyParser.json());


app.get('/', (req, res) => {
  res.send('Server is running');
});

// Connection URI and options
const uri = 'mongodb+srv://rushaid4:root12345@conversational.9ik2tt0.mongodb.net/';


// Connect to MongoDB
mongoose.connect(uri);

// Connection events
mongoose.connection.on('connected', () => {
  console.log('Mongoose connected to MongoDB successfully');
});

mongoose.connection.on('error', (err) => {
  console.error('Mongoose connection error:', err);
});

mongoose.connection.on('disconnected', () => {
  console.log('Mongoose disconnected from MongoDB');
});

const userSchema = new mongoose.Schema({
  username: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});

const User = mongoose.model('User', userSchema);

const itemSchema = new mongoose.Schema({
  name: { type: String, required: true },
  price: { type: Number, required: true },
}, { collection: 'items' });

const Item = mongoose.model('Item', itemSchema);

const authenticate = (req, res, next) => {

  const authHeader = req.header('Authorization');
  console.log("Authorization Header:", authHeader); // Log the Authorization header

  if (!authHeader) {
    return res.status(401).json({ success: false, errors: 'No token, authorization denied' });
  }

  const token = req.header('Authorization').replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ success: false, errors: 'No token, authorization denied' });
  }
  try {
    console.log("Received token:", token);
    const decoded = jwt.verify(token, JWT_SECRET);
    console.log("Decoded token:", decoded);
    req.user = decoded.user.id;
    next();
  } catch (err) {
    console.error('Token verification error:', err); 
    res.status(401).json({ success: false, errors: 'Token is not valid' });
  }
};


app.post('/signup', async (req, res) => {
  const { username, email, password } = req.body;
  try {
    const user = new User({ username, email, password});
    await user.save();
    // const token = jwt.sign({ userId: user._id }, JWT_SECRET);
    const token = jwt.sign({ user: { id: user._id } }, JWT_SECRET);
    res.json({ success: true, token });
  } catch (err) {
    res.json({ success: false, errors: err.message });
  }
});

app.post('/login', async (req, res) => {
  console.log("INSIDE LOGIN ENDPOINT")
  let user = await User.findOne({ email: req.body.email });
  console.log(user)
  if (user) {
    console.log("inside user")
    console.log(req.body.password)
    console.log(user.password)
    const passCompare = req.body.password === user.password;
    if (passCompare) {
      const data = {
        user: {
          id: user.id
        }
      };
      // const token = jwt.sign(data, 'secret_ecom');
      const token = jwt.sign({ user: { id: user._id } }, JWT_SECRET);
      res.json({ success: true, token });
    } else {
      res.json({ success: false, error: "Wrong password" });
    }
  } else {
    res.json({ success: false, errors: "Wrong email ID" });
  }
});


// app.post('/add-item', authenticate, async (req, res) => {
//   const { name, price } = req.body;
//   const item = new Item({ name, price });
//   try {
//     await item.save();
//     res.json({ success: true, item });
//   } catch (err) {
//     res.json({ success: false, errors: err.message });
//   }
// });
app.post('/add-item', authenticate, async (req, res) => {



  console.log("inside add item")
  // Destructure the request body to get name and price
  let { name, price } = req.body;
  console.log(name)
  console.log(price)

  // Trim leading and trailing spaces and convert the item name to lowercase
  name = name.trim().toLowerCase();

  // Trim leading and trailing spaces from price
  price = price.toString().trim();

  // Create a new item instance with the cleaned-up data
  const item = new Item({ name, price });

  try {
    // Save the item to the database
    await item.save();
    
    // Respond with success message and the saved item
    res.json({ success: true, item });
  } catch (err) {
    // Respond with error message if saving fails
    res.json({ success: false, errors: err.message });
  }
});


app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

