using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    public bool MatchEnded { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
    }

    public void EndMatch(Team losingTeam)
    {
        if (MatchEnded) return;

        MatchEnded = true;
        Team winner = losingTeam == Team.Blue ? Team.Red : Team.Blue;

        Debug.Log($"Fim de jogo! Vencedor: {winner}");
        Time.timeScale = 0f;
    }

    public void RestartMatch()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }
}
