// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Diego Araque
// Marco Torres
// Fer Valdeón 
// November 2022

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

// Object to store agent position
[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

// Object to store agents data
[Serializable]
public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour
{
    // Urls
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string getBoxesEndpoint = "/getBoxes";
    string getDestinyEndpoint = "/getDestiny";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";

    // Agents darta
    AgentsData agentsData, obstacleData, boxData, destinyData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;

    // Model data
    public int NAgents, width, height, boxes;
    public float timeToUpdate = 5.0f;
    private float timer, dt;
    bool updated = false, agents_started = false, boxs_started = false;
    public GameObject agentPrefab, obstaclePrefab, destinyPrefab, boxPrefab, floor;

    void Start()
    {
        // Init objects
        agentsData = new AgentsData();
        obstacleData = new AgentsData();
        boxData = new AgentsData();
        destinyData = new AgentsData();

        // Agent dictionary
        agents = new Dictionary<string, GameObject>();
        
        // Positions
        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        floor.transform.localScale = new Vector3((float) width/10, 1, (float) height/10);
        floor.transform.localPosition = new Vector3((float) width/2-0.5f, 0, (float) height/2-0.5f);
        timer = timeToUpdate;

        // Configurate model
        StartCoroutine(SendConfiguration());
    }


    private void Update() 
    {
        // When the agents arrived to their new positions
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }
        // Move objects to their new positions
        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach (var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;
                
                // Only rotate agents (with ids from 1000 to 1999), boxes rotation will remain the same
                if (int.Parse(agent.Key) < 2000)
                    if (direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
        }
    }
 

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Get new positions
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetBoxData());
            StartCoroutine(GetDestinyData());
        }
    }


    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        // Model params
        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());
        form.AddField("boxes", boxes.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration completed!");
            Debug.Log("Getting agents positions...");

            // Get agents positions
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetBoxData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetDestinyData());
        }
    }


    IEnumerator GetAgentsData() 
    {
        // Get agents positions
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach (AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                // If its the first step
                if (!agents_started)
                {
                    prevPositions[agent.id] = newAgentPosition; // New positions will be previous
                    agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, Quaternion.identity); // Set game object
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    if (currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition; // Current position will be previous
                    currPositions[agent.id] = newAgentPosition; // New position will be current
                }
            }
            updated = true;
            if (!agents_started) agents_started = true;
        }
    }


    IEnumerator GetBoxData() 
    {
        // Get boxs positions
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            boxData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach(AgentData box in boxData.positions)
            {
                Vector3 newBoxPosition = new Vector3(box.x, box.y, box.z);
                    // If its the first step
                    if (!boxs_started)
                    {
                        prevPositions[box.id] = newBoxPosition; // New positions will be previous
                        agents[box.id] = Instantiate(boxPrefab, newBoxPosition, Quaternion.identity); // Set game object
                    }
                    else
                    {
                        Vector3 currentPosition = new Vector3();
                        if (currPositions.TryGetValue(box.id, out currentPosition))
                            prevPositions[box.id] = currentPosition; // Current position will be previous
                        currPositions[box.id] = newBoxPosition; // New position will be current
                    }
            }
            updated = true;
            if (!boxs_started) boxs_started = true;
        }
    }


    IEnumerator GetDestinyData() 
    {
        // Get destinations positions
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDestinyEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            destinyData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach (AgentData destiny in destinyData.positions)
            {
                Instantiate(destinyPrefab, new Vector3(destiny.x, destiny.y, destiny.z), Quaternion.identity);
            }
        }
    }


    IEnumerator GetObstacleData() 
    {
        // Get obtacles positions
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach(AgentData obstacle in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
            }
        }
    }
}
