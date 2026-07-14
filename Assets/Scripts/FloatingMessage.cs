using UnityEngine;

public sealed class FloatingMessage : MonoBehaviour
{
    [SerializeField] private float amplitude = 0.35f;
    [SerializeField] private float speed = 1.2f;
    [SerializeField] private float rotationAmount = 4f;

    private Vector3 startPosition;
    private Quaternion startRotation;
    private float phase;

    private void Awake()
    {
        startPosition = transform.position;
        startRotation = transform.rotation;
        phase = Random.value * Mathf.PI * 2f;
    }

    private void Update()
    {
        float wave = Mathf.Sin(Time.time * speed + phase);
        transform.position = startPosition + Vector3.up * wave * amplitude;
        transform.rotation = startRotation * Quaternion.Euler(0f, wave * rotationAmount, wave * rotationAmount * 0.35f);
    }
}
