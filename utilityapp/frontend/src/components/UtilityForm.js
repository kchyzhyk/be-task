import React, { useState } from "react";
import axios from "axios"; // Import Axios

const UtilityForm = () => {
  // Set state for form inputs and API response
  const [address, setAddress] = useState("");
  const [consumption, setConsumption] = useState("");
  const [escalator, setEscalator] = useState(4);
  const [tariffData, setTariffData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Make the API call to Django backend
      const response = await axios.get("http://localhost:8000/api/get_tariff_data/", {
        params: {
          address: address,
          consumption_kwh: consumption,
          escalator_percentage: escalator
        }
      });

      // Set the response data in state
      setTariffData(response.data);
    } catch (error) {
      console.error("There was an error fetching the data!", error);
    }

    setLoading(false);
  };

  return (
    <div>
      <h1>Utility Rate Form</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Address:</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            required
          />
        </div>
        <div>
          <label>kWh Consumption:</label>
          <input
            type="number"
            min="1000"
            max="10000"
            value={consumption}
            onChange={(e) => setConsumption(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Escalator Percentage (4% - 10%):</label>
          <input
            type="number"
            value={escalator}
            onChange={(e) => setEscalator(e.target.value)}
            min="4"
            max="10"
            required
          />
        </div>
        <button type="submit">Get Tariff Data</button>
      </form>

      {loading && <p>Loading...</p>}

      {tariffData && (
        <div>
          <h3>Tariff Data:</h3>
          <p><strong>Most Likely Tariff:</strong> {tariffData.tariff_name}</p>
          <p><strong>Price (¢/kWh):</strong> {tariffData.price_per_kwh}</p>
          <p><strong>Full Tariff List:</strong></p>
          <ul>
            {tariffData.full_tariff_list.map((tariff, index) => (
              <li key={index}>{tariff.name} - {tariff.price}¢/kWh</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default UtilityForm;
