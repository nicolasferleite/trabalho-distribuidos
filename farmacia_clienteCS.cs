using System;
using System.Collections.Generic;
using System.Drawing;
using System.Net.Http;
using System.Net.Http.Json;
using System.Windows.Forms;
using System.Threading.Tasks;

namespace PharmacyClient;

// Modelo (Deve ter nomes iguais ao JSON do Python)
public class Medicine {
    public int id { get; set; }
    public string name { get; set; }
    public float price { get; set; }
    public int quantity { get; set; }
    public string category { get; set; }
}

public class PharmacyForm : Form {
    private const string API_URL = "http://localhost:8000";
    private readonly HttpClient client = new HttpClient();
    
    // Componentes UI
    private DataGridView grid;
    private Button btnSell;
    private Button btnRefresh;
    private Label lblStatus;

    public PharmacyForm() {
        this.Text = "PDV - Caixa Farmácia (C#)";
        this.Size = new Size(600, 500);
        
        SetupUI();
        _ = LoadData(); // Carrega dados ao iniciar
    }

    private void SetupUI() {
        // Grid de Produtos
        grid = new DataGridView { 
            Location = new Point(10, 10), 
            Size = new Size(560, 350),
            AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
            SelectionMode = DataGridViewSelectionMode.FullRowSelect,
            MultiSelect = false,
            ReadOnly = true
        };

        // Botão Vender
        btnSell = new Button { 
            Text = "VENDER (-1 unid)", 
            Location = new Point(10, 370), 
            Size = new Size(150, 40),
            BackColor = Color.LightGreen 
        };
        btnSell.Click += async (s, e) => await SellSelectedItem();

        // Botão Atualizar
        btnRefresh = new Button { 
            Text = "Atualizar Lista", 
            Location = new Point(170, 370), 
            Size = new Size(120, 40) 
        };
        btnRefresh.Click += async (s, e) => await LoadData();

        // Label Status
        lblStatus = new Label { 
            Text = "Pronto.", 
            Location = new Point(10, 420), 
            AutoSize = true,
            ForeColor = Color.Blue
        };

        this.Controls.Add(grid);
        this.Controls.Add(btnSell);
        this.Controls.Add(btnRefresh);
        this.Controls.Add(lblStatus);
    }

    private async Task LoadData() {
        try {
            var meds = await client.GetFromJsonAsync<List<Medicine>>($"{API_URL}/medicines");
            grid.DataSource = meds;
            lblStatus.Text = $"Dados carregados: {DateTime.Now.ToShortTimeString()}";
        } catch {
            lblStatus.Text = "Erro: API Offline?";
            lblStatus.ForeColor = Color.Red;
        }
    }

    private async Task SellSelectedItem() {
        if (grid.SelectedRows.Count == 0) return;

        // Pega o objeto Medicine da linha selecionada
        var med = (Medicine)grid.SelectedRows[0].DataBoundItem;

        try {
            // Chama a rota de venda (baixa 1 no estoque)
            var response = await client.PostAsync($"{API_URL}/sell/{med.id}/1", null);
            
            if (response.IsSuccessStatusCode) {
                lblStatus.Text = $"Venda realizada: {med.name}";
                await LoadData(); // Recarrega para ver o estoque novo
            } else {
                MessageBox.Show("Erro ao vender! Estoque vazio?");
            }
        } catch (Exception ex) {
            MessageBox.Show($"Erro de conexão: {ex.Message}");
        }
    }

    [STAThread]
    static void Main() {
        Application.EnableVisualStyles();
        Application.Run(new PharmacyForm());
    }
}