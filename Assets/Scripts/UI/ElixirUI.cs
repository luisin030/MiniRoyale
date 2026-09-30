using TMPro;
using UnityEngine;

public class ElixirUI : MonoBehaviour
{
    [SerializeField] private ElixirSystem elixirSystem;
    [SerializeField] private TMP_Text elixirText;

    private void OnEnable()
    {
        if (elixirSystem != null)
            elixirSystem.OnElixirChanged += UpdateText;
    }

    private void Start()
    {
        if (elixirText != null)
            elixirText.text = "Elixir";
    }

    private void OnDisable()
    {
        if (elixirSystem != null)
            elixirSystem.OnElixirChanged -= UpdateText;
    }

    private void UpdateText(float current, float max)
    {
        if (elixirText != null)
            elixirText.text = $"Elixir: {current:0.0}/{max:0}";
    }
}
