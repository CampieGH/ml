using UnityEngine;

public sealed class GlitchPulse : MonoBehaviour
{
    [SerializeField] private float positionJitter = 0.08f;
    [SerializeField] private float scaleJitter = 0.12f;
    [SerializeField] private float pulseSpeed = 7f;
    [SerializeField] private float glitchChance = 0.08f;

    private Vector3 startPosition;
    private Vector3 startScale;
    private Renderer cachedRenderer;
    private MaterialPropertyBlock block;

    private void Awake()
    {
        startPosition = transform.localPosition;
        startScale = transform.localScale;
        cachedRenderer = GetComponent<Renderer>();
        block = new MaterialPropertyBlock();
    }

    private void Update()
    {
        float pulse = 1f + Mathf.Sin(Time.time * pulseSpeed + transform.position.sqrMagnitude) * scaleJitter;
        transform.localScale = startScale * pulse;

        if (Random.value < glitchChance)
        {
            transform.localPosition = startPosition + Random.insideUnitSphere * positionJitter;
        }
        else
        {
            transform.localPosition = Vector3.Lerp(transform.localPosition, startPosition, Time.deltaTime * 14f);
        }

        if (cachedRenderer != null)
        {
            cachedRenderer.GetPropertyBlock(block);
            block.SetFloat("_Glitch", Random.value < glitchChance ? Random.Range(0.35f, 1f) : 0f);
            cachedRenderer.SetPropertyBlock(block);
        }
    }
}
