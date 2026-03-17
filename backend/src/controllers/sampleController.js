// Sample controller
exports.getSample = async (req, res) => {
    try {
        res.json({ message: 'Controller working' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};
