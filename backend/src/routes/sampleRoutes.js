const express = require('express');
const router = express.Router();
const { getSample } = require('../controllers/sampleController');

router.get('/', getSample);

module.exports = router;
