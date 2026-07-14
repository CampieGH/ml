#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using TMPro;

public static class DigicoreSceneGenerator
{
    private const string ScenePath = "Assets/Scenes/DigicoreDream.unity";

    [MenuItem("Tools/ML/Generate Digicore Dream")]
    public static void Generate()
    {
        EnsureFolder("Assets/Scenes");
        EnsureFolder("Assets/Materials");

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        RenderSettings.fog = true;
        RenderSettings.fogMode = FogMode.ExponentialSquared;
        RenderSettings.fogDensity = 0.012f;
        RenderSettings.fogColor = new Color(0.15f, 0.01f, 0.24f);
        RenderSettings.ambientMode = AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.55f, 0.02f, 0.72f);
        RenderSettings.ambientEquatorColor = new Color(0.18f, 0.01f, 0.32f);
        RenderSettings.ambientGroundColor = new Color(0.04f, 0f, 0.08f);

        Material ground = Mat("DreamGround", new Color(0.13f, 0.01f, 0.23f), new Color(0.45f, 0f, 0.7f) * 2.2f);
        Material grass = Mat("NeonGrass", new Color(0.55f, 0.02f, 0.75f), new Color(0.9f, 0.02f, 1f) * 2.5f);
        Material pink = Mat("HotPink", new Color(1f, 0.02f, 0.55f), new Color(1f, 0.01f, 0.38f) * 4f);
        Material cyan = Mat("DreamCyan", new Color(0.05f, 0.65f, 1f), new Color(0.05f, 0.8f, 1f) * 4f);
        Material yellow = Mat("AcidYellow", new Color(1f, 0.72f, 0.01f), new Color(1f, 0.55f, 0f) * 3f);
        Material black = Mat("VoidBlack", new Color(0.01f, 0f, 0.025f), Color.black);

        var world = new GameObject("DIGICORE_DREAM");
        Block("Ground", Vector3.down * 0.45f, new Vector3(70f, 0.8f, 70f), ground, world.transform);

        Random.InitState(404);
        for (int i = 0; i < 420; i++)
        {
            Vector3 p = new Vector3(Random.Range(-30f, 30f), 0.35f, Random.Range(-30f, 30f));
            GameObject blade = Block("Grass", p, new Vector3(Random.Range(.07f,.18f), Random.Range(.7f,2.3f), Random.Range(.07f,.18f)), grass, world.transform);
            blade.transform.rotation = Quaternion.Euler(Random.Range(-8f,8f), Random.Range(0f,360f), Random.Range(-8f,8f));
        }

        CreateFlower(new Vector3(-4f, 1.8f, 5f), 3.4f, pink, yellow, world.transform);
        CreateFlower(new Vector3(5f, 1.2f, 8f), 2.5f, cyan, yellow, world.transform);
        CreateFlower(new Vector3(10f, 1.5f, -3f), 3f, pink, cyan, world.transform);

        for (int i = 0; i < 16; i++)
        {
            Vector3 p = new Vector3(Random.Range(-26f, 26f), Random.Range(2f, 11f), Random.Range(-20f, 25f));
            var shard = Block("GlitchShard", p, new Vector3(Random.Range(.4f,2.2f), Random.Range(.2f,1f), Random.Range(.4f,2.5f)), i % 2 == 0 ? cyan : pink, world.transform);
            shard.transform.rotation = Random.rotation;
            shard.AddComponent<FloatingMessage>();
        }

        CreateMessage("// SYSTEM ONLINE", new Vector3(-7f, 5.5f, 7f), cyan, world.transform);
        CreateMessage("WHO ARE YOU?", new Vector3(5f, 4.4f, 11f), pink, world.transform);
        CreateMessage("IT'S BEAUTIFUL, BUT IT HURTS", new Vector3(8f, 6.2f, -1f), cyan, world.transform);
        CreateMessage("YOU ARE NOT SUPPOSED TO BE HERE", new Vector3(-8f, 8f, -3f), pink, world.transform);

        var player = new GameObject("PlayerPlaceholder");
        player.transform.position = new Vector3(0f, 1f, -4f);
        Block("Body", player.transform.position + Vector3.up * .6f, new Vector3(1.1f, 1.5f, .7f), black, player.transform);
        Sphere("Head", player.transform.position + Vector3.up * 1.75f, .55f, cyan, player.transform);
        Block("LegL", player.transform.position + new Vector3(-.28f,-.45f,0), new Vector3(.35f,.9f,.35f), black, player.transform);
        Block("LegR", player.transform.position + new Vector3(.28f,-.45f,0), new Vector3(.35f,.9f,.35f), black, player.transform);

        var sunObj = new GameObject("Pink Sun");
        var sun = sunObj.AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.color = new Color(1f, .12f, .75f);
        sun.intensity = 1.4f;
        sunObj.transform.rotation = Quaternion.Euler(38f, -28f, 0f);

        Point("Cyan Fill", new Vector3(-7f,5f,-2f), new Color(.1f,.65f,1f), 30f, 20f);
        Point("Pink Fill", new Vector3(7f,4f,5f), new Color(1f,.02f,.45f), 34f, 18f);

        var volumeObj = new GameObject("Global Volume");
        var volume = volumeObj.AddComponent<Volume>();
        volume.isGlobal = true;
        volume.profile = ScriptableObject.CreateInstance<VolumeProfile>();
        var bloom = volume.profile.Add<Bloom>();
        bloom.intensity.Override(1.7f);
        bloom.threshold.Override(.7f);
        var chroma = volume.profile.Add<ChromaticAberration>();
        chroma.intensity.Override(.35f);
        var vignette = volume.profile.Add<Vignette>();
        vignette.intensity.Override(.3f);
        var color = volume.profile.Add<ColorAdjustments>();
        color.saturation.Override(35f);
        color.contrast.Override(20f);

        var camObj = new GameObject("Main Camera");
        camObj.tag = "MainCamera";
        var cam = camObj.AddComponent<Camera>();
        cam.fieldOfView = 55f;
        camObj.transform.position = new Vector3(0f, 4.2f, -12f);
        camObj.transform.LookAt(new Vector3(0f, 2.3f, 5f));

        EditorSceneManager.SaveScene(scene, ScenePath);
        AssetDatabase.SaveAssets();
        Selection.activeGameObject = world;
        Debug.Log("Generated " + ScenePath);
    }

    private static void CreateFlower(Vector3 p, float scale, Material petals, Material stem, Transform parent)
    {
        var root = new GameObject("DreamFlower"); root.transform.SetParent(parent); root.transform.position = p;
        Block("Stem", p + Vector3.up * scale, new Vector3(.25f, scale * 2f, .25f), stem, root.transform);
        Sphere("Core", p + Vector3.up * scale * 2f, .5f * scale, stem, root.transform);
        for (int i=0;i<6;i++)
        {
            float a = i * 60f * Mathf.Deg2Rad;
            Vector3 q = p + Vector3.up * scale * 2f + new Vector3(Mathf.Cos(a),0,Mathf.Sin(a)) * scale * .75f;
            var petal = Sphere("Petal", q, .65f * scale, petals, root.transform);
            petal.transform.localScale = new Vector3(1.2f,.45f,.8f);
        }
    }

    private static void CreateMessage(string text, Vector3 p, Material mat, Transform parent)
    {
        var go = new GameObject("Message_" + text);
        go.transform.SetParent(parent); go.transform.position = p; go.transform.rotation = Quaternion.Euler(0,180,0);
        var tmp = go.AddComponent<TextMeshPro>();
        tmp.text = text; tmp.fontSize = 2.2f; tmp.alignment = TextAlignmentOptions.Center; tmp.color = Color.white;
        tmp.outlineWidth = .18f; tmp.outlineColor = mat.color;
        go.AddComponent<FloatingMessage>();
    }

    private static GameObject Block(string n, Vector3 p, Vector3 s, Material m, Transform parent)
    { var g=GameObject.CreatePrimitive(PrimitiveType.Cube); g.name=n; g.transform.SetParent(parent); g.transform.position=p; g.transform.localScale=s; g.GetComponent<Renderer>().sharedMaterial=m; return g; }
    private static GameObject Sphere(string n, Vector3 p, float s, Material m, Transform parent)
    { var g=GameObject.CreatePrimitive(PrimitiveType.Sphere); g.name=n; g.transform.SetParent(parent); g.transform.position=p; g.transform.localScale=Vector3.one*s; g.GetComponent<Renderer>().sharedMaterial=m; return g; }
    private static void Point(string n, Vector3 p, Color c, float intensity, float range)
    { var g=new GameObject(n); g.transform.position=p; var l=g.AddComponent<Light>(); l.type=LightType.Point; l.color=c; l.intensity=intensity; l.range=range; }

    private static Material Mat(string name, Color baseColor, Color emission)
    {
        string path="Assets/Materials/"+name+".mat";
        var existing=AssetDatabase.LoadAssetAtPath<Material>(path); if(existing!=null)return existing;
        Shader shader=Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
        var m=new Material(shader); m.color=baseColor; m.EnableKeyword("_EMISSION"); m.SetColor("_EmissionColor", emission); m.SetFloat("_Smoothness", .55f);
        AssetDatabase.CreateAsset(m,path); return m;
    }

    private static void EnsureFolder(string path)
    {
        string[] parts=path.Split('/'); string current=parts[0];
        for(int i=1;i<parts.Length;i++){ string next=current+"/"+parts[i]; if(!AssetDatabase.IsValidFolder(next))AssetDatabase.CreateFolder(current,parts[i]); current=next; }
    }
}
#endif
