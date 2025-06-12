const express = require("express");
const bodyParser = require('body-parser');

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended : false}));
app.use(express.json());
app.use(express.urlencoded({extended : true}));

// simple api
app.get("/", (req, res) => {
  res.send("Hello World!!");
});

// post, request body, response O
app.get("/get-sensor", (req, res) => {
  const temperature = req.query.temperature;
  console.log("value : "+temperature);
  res.json({ok:"get", value : temperature});
})

// post, request body, response O
app.post("/post-sensor", (req, res) => {
  const { sensor_number, value } = req.body;
  console.log("sensor_number : "+sensor_number+" / value : "+value);
  res.json({ok:"post", sensor_number:sensor_number, value : value});
})

module.exports = app;