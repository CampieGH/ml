#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

[InitializeOnLoad]
public static class PrototypeSceneGenerator
{
    private const string ScenePath = "Assets/Scenes/Prototype.unity";
    private const string GeneratedFlag = "ML_PrototypeSceneGenerated";

    static PrototypeSceneGenerator()
    {
        EditorApplication.delayCall += GenerateOnce;
    }

    [MenuItem("Tools/ML/Regenerate Prototype Scene")]
    public static void GenerateScene()
    {
        if (!AssetDatabase.IsValidFolder("Assets/Scenes"))
        {
            AssetDatabase.CreateFolder("Assets", "Scenes");
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        RenderSettings.ambientMode = AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.21f, 0.28f, 0.40f);
        RenderSettings.ambientEquatorColor = new Color(0.11f, 0.13f, 0.18f);
        RenderSettings.ambientGroundColor = new Color(0.035f, 0.04f, 0.055f);
        RenderSettings.fog = true;
        RenderSettings.fogColor = new Color(0.07f, 0.09f, 0.13f);
        RenderSettings.fogMode = FogMode.ExponentialSquared;
        RenderSettings.fogDensity = 0.018f;

        Material ground = CreateMaterial("Ground", new Color(0.055f, 0.065f, 0.085f), 0.1f, 0.45f);
        Material concrete = CreateMaterial("Concrete", new Color(0.22f, 0.25f, 0.30f), 0.05f, 0.32f);
        Material accent = CreateMaterial("Accent", new Color(0.95f, 0.28f, 0.12f), 0.05f, 0.4f);
        Material glass = CreateMaterial("Glass", new Color(0.08f, 0.55f, 0.75f), 0.25f, 0.8f);
        Material dark = CreateMaterial("Dark", new Color(0.025f, 0.03f, 0.045f), 0.2f, 0.5f);

        GameObject root = new GameObject("Prototype Environment");

        CreateBlock("Ground", new Vector3(0f, -0.5f, 0f), new Vector3(46f, 1f, 46f), ground, root.transform);
        CreateBlock("Central Platform", new Vector3(0f, 0.25f, 0f), new Vector3(15f, 0.5f, 12f), concrete, root.transform);
        CreateBlock("Accent Strip", new Vector3(0f, 0.56f, 0f), new Vector3(1.1f, 0.08f, 12.2f), accent, root.transform);

        CreateBuilding(new Vector3(-11f, 3f, 4f), new Vector3(6f, 6f, 9f), concrete, glass, root.transform);
        CreateBuilding(new Vector3(11f, 4.5f, 2f), new Vector3(7f, 9f, 8f), dark, glass, root.transform);
        CreateBuilding(new Vector3(6f, 2.25f, -11f), new Vector3(10f, 4.5f, 5f), concrete, accent, root.transform);

        for (int i = 0; i < 6; i++)
        {
            float x = -12.5f + i * 5f;
            CreateBlock($"Pillar {i + 1}", new Vector3(x, 2f, -16f), new Vector3(0.7f, 4f, 0.7f), dark, root.transform);
            CreateBlock($"Pillar Light {i + 1}", new Vector3(x, 4.15f, -16f), new Vector3(0.9f, 0.16f, 0.9f), accent, root.transform);
        }

        GameObject focus = CreateBlock("Focus Monument", new Vector3(0f, 2.2f, 0f), new Vector3(2.2f, 4.4f, 2.2f), dark, root.transform);
        CreateBlock("Monument Core", new Vector3(0f, 2.2f, -1.14f), new Vector3(1.1f, 2.7f, 0.12f), accent, focus.transform);

        var sunObject = new GameObject("Sun");
        var sun = sunObject.AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.color = new Color(1f, 0.79f, 0.64f);
        sun.intensity = 2.1f;
        sun.shadows = LightShadows.Soft;
        sunObject.transform.rotation = Quaternion.Euler(42f, -32f, 0f);

        CreatePointLight("Blue Fill", new Vector3(-8f, 5f, -2f), new Color(0.1f, 0.5f, 1f), 8f, 16f);
        CreatePointLight("Orange Fill", new Vector3(8f, 4f, 5f), new Color(1f, 0.25f, 0.08f), 7f, 14f);

        var cameraObject = new GameObject("Main Camera");
        cameraObject.tag = "MainCamera";
        var camera = cameraObject.AddComponent<Camera>();
        camera.fieldOfView = 52f;
        camera.nearClipPlane = 0.1f;
        camera.farClipPlane = 250f;
        cameraObject.transform.position = new Vector3(19f, 13f, -21f);
        cameraObject.transform.LookAt(focus.transform.position + Vector3.up * 1.5f);
        var orbit = cameraObject.AddComponent<OrbitCamera>();
        orbit.SetTarget(focus.transform);

        EditorSceneManager.SaveScene(scene, ScenePath);
        Selection.activeGameObject = focus;
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log($"Generated prototype scene at {ScenePath}");
    }

    private static void GenerateOnce()
    {
        if (SessionState.GetBool(GeneratedFlag, false))
        {
            return;
        }

        SessionState.SetBool(GeneratedFlag, true);
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
        {
            GenerateScene();
        }
    }

    private static GameObject CreateBlock(string name, Vector3 position, Vector3 scale, Material material, Transform parent)
    {
        GameObject block = GameObject.CreatePrimitive(PrimitiveType.Cube);
        block.name = name;
        block.transform.SetParent(parent);
        block.transform.position = position;
        block.transform.localScale = scale;
        block.GetComponent<Renderer>().sharedMaterial = material;
        return block;
    }

    private static void CreateBuilding(Vector3 position, Vector3 scale, Material body, Material window, Transform parent)
    {
        GameObject building = CreateBlock("Building", position, scale, body, parent);
        float frontZ = position.z - scale.z * 0.505f;

        for (int floor = 0; floor < Mathf.Max(1, Mathf.FloorToInt(scale.y / 2f)); floor++)
        {
            float y = position.y - scale.y * 0.35f + floor * 1.6f;
            CreateBlock("Window", new Vector3(position.x, y, frontZ), new Vector3(scale.x * 0.68f, 0.65f, 0.08f), window, building.transform);
        }
    }

    private static void CreatePointLight(string name, Vector3 position, Color color, float intensity, float range)
    {
        var lightObject = new GameObject(name);
        lightObject.transform.position = position;
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Point;
        light.color = color;
        light.intensity = intensity;
        light.range = range;
        light.shadows = LightShadows.Soft;
    }

    private static Material CreateMaterial(string name, Color color, float metallic, float smoothness)
    {
        const string folder = "Assets/Materials";
        if (!AssetDatabase.IsValidFolder(folder))
        {
            AssetDatabase.CreateFolder("Assets", "Materials");
        }

        string path = $"{folder}/{name}.mat";
        Material existing = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (existing != null)
        {
            return existing;
        }

        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
        {
            shader = Shader.Find("Standard");
        }

        var material = new Material(shader)
        {
            name = name,
            color = color
        };
        material.SetFloat("_Metallic", metallic);
        material.SetFloat("_Smoothness", smoothness);
        AssetDatabase.CreateAsset(material, path);
        return material;
    }
}
#endif
