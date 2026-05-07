# 🔍 Auditor IA - Sistema de Auditoría Automática de Seguros

Un sistema inteligente de auditoría de seguros que utiliza **Google Gemini** para analizar, verificar y recomendar aprobación o rechazo de reclamos de seguros.

## 🎯 Características Principales

- ✅ **Análisis inteligente de reclamos** usando Google Gemini AI
- ✅ **Verificación automática de coberturas** según pólizas
- ✅ **Consulta de tarifarios** y políticas de seguros
- ✅ **Interfaz amigable** con Streamlit
- ✅ **Historial de conversaciones** persistente
- ✅ **Base de datos simulada** con casos reales

## 📋 Estructura del Proyecto

```
auditor-agente-ia/
├── venv/                   # Entorno virtual de Python
├── .env                    # Variables de entorno (API KEY)
├── .gitignore              # Archivos a ignorar en Git
├── requirements.txt        # Dependencias del proyecto
├── database.py             # Datos simulados (Tarifarios y Siniestros)
├── agente.py              # Lógica del agente Gemini
├── app.py                 # Interfaz de usuario (Streamlit)
└── README.md              # Este archivo
```

## 🚀 Inicio Rápido

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/auditor-agente-ia.git
cd auditor-agente-ia
```

### 2. Crear el entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En macOS/Linux
# o
venv\Scripts\activate  # En Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la API KEY
1. Obtén tu API KEY de Google Gemini en [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea un archivo `.env` en la raíz del proyecto:
   ```
   GEMINI_API_KEY=tu_api_key_aqui
   ```

### 5. Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## 📚 Cómo Usar

### Ejemplo 1: Consultar Tarifarios
```
Usuario: ¿Cuáles son las coberturas disponibles para seguros de auto?
```

### Ejemplo 2: Analizar un Siniestro
```
Usuario: Analiza el siniestro SIN001 y dame tu recomendación
```

### Ejemplo 3: Consultar Políticas
```
Usuario: ¿Cuáles son los criterios de rechazo en auditoría?
```

## 🛠️ Herramientas Disponibles

El agente tiene acceso a las siguientes herramientas:

| Herramienta | Descripción |
|------------|-----------|
| `obtener_tarifario` | Obtiene información de tarifarios de seguros |
| `obtener_siniestro` | Obtiene detalles de un siniestro específico |
| `listar_siniestros` | Lista todos los siniestros disponibles |
| `obtener_politicas` | Obtiene las políticas de auditoría |

## 📊 Base de Datos

### Tipos de Seguros Disponibles
- **Auto**: Responsabilidad Civil, Daños Propios, Cobertura Integral
- **Hogar**: Incendio y Robo, Incendio + Daños por agua

### Siniestros de Ejemplo
- SIN001: Choque frontal (Auto)
- SIN002: Robo (Hogar)
- SIN003: Daño por granizo (Auto)
- SIN004: Responsabilidad civil (Auto)
- SIN005: Incendio (Hogar)

## 🔐 Seguridad

- ⚠️ **NUNCA** subas el archivo `.env` a GitHub
- El archivo `.gitignore` está configurado para ignorarlo automáticamente
- Tu API KEY está protegida localmente

## 📦 Dependencias

- `streamlit`: Framework para la interfaz web
- `google-generativeai`: API de Google Gemini
- `python-dotenv`: Gestión de variables de entorno
- `requests`: Librería HTTP
- `pandas`: Manipulación de datos

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👤 Autor

- **Tu Nombre** - *Trabajo Inicial* - [GitHub](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Google por la API de Gemini
- Streamlit por el framework de interfaz
- La comunidad de Python

## 📞 Soporte

Si tienes preguntas o encontraste un bug, por favor abre un [Issue](https://github.com/tu-usuario/auditor-agente-ia/issues).

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub! ⭐
