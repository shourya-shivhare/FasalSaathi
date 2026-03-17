const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());

// Error Handler (must be imported after routes)
const errorHandler = require('./src/middleware/errorHandler');

// Routes
const sampleRoutes = require('./src/routes/sampleRoutes');
app.use('/api/sample', sampleRoutes);

// Backend → AI Service health check
app.get('/api/ai-health', async (req, res) => {
    try {
        const response = await axios.get(`${AI_SERVICE_URL}/`);
        res.json({ aiService: response.data });
    } catch (err) {
        res.status(500).json({ error: 'AI service unreachable', details: err.message });
    }
});

app.get('/', (req, res) => {
    res.send('FasalSaathi Backend API is running...');
});

// Global Error Handler
app.use(errorHandler);

// Start Server
app.listen(PORT, () => {
    console.log(`Server started on http://localhost:${PORT}`);
});
