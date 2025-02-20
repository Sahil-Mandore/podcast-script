import React, { useState } from "react";
import axios from "axios";

function ScriptForm() {
  const [topic, setTopic] = useState("");
   const [duration, setDuration] = useState(5);
  const [tone, setTone] = useState("conversational");
  const [format, setFormat] = useState("linkedin");
  const [temperature, setTemperature] = useState(0.7);
  //const [sources, setSources] = useState([]);
  const [script, setScript] = useState("");
  const [loading, setLoading] = useState(false);

  const formatOptions = {
    "LinkedIn post": "linkedin",
    "Instagram caption": "instagram",
    "YouTube description": "youtube_desc",
    "Monologue": "monologue",
    "Interview": "interview"
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/generate_script/", {
        topic,
        tone,
        format,
        temperature,
        search_tool: "duckduckgo" // Defaulting to DuckDuckGo, can be changed
        //search_tools: ["duckduckgo", "googlesearch"]
      });

      if (response.status === 200) {
        setScript(response.data.script);
        //setSources(response.data.sources || []);
      } else {
        console.error("Unexpected API response:", response);
      }
    } catch (error) {
      console.error("Axios request failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Topic:</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a topic"
          />
        </div>
        <div>
          <label>Tone:</label>
          <select value={tone} onChange={(e) => setTone(e.target.value)}>
            <option value="conversational">Conversational</option>
            <option value="formal">Formal</option>
            <option value="humorous">Humorous</option>
          </select>
        </div>
        <div>
          <label>Format:</label>
          <select value={format} onChange={(e) => setFormat(e.target.value)}>
            {Object.keys(formatOptions).map((key) => (
              <option key={key} value={formatOptions[key]}>
                {key}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Variation Level (Temperature):</label>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
          />
        </div>
        <div>
          <label>Duration (minutes):</label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            min="1"
            max="60"
          />
           </div>
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Script"}
        </button>
      </form>

      {script && (
        <div>
          <h2>Generated Script:</h2>
          <textarea value={script} readOnly rows="50" cols="50" />
        </div>
      )}
    </div>
  );
}

export default ScriptForm;
