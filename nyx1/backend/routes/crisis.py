from fastapi import APIRouter

router = APIRouter()

DEMO_HELPLINES = [
    {
        "name": "Tele MANAS (Demo)",
        "number": "14416-DEMO",
        "real_number": "14416",
        "available": "24/7",
        "languages": "22 languages",
    },
    {
        "name": "KIRAN Helpline (Demo)",
        "number": "1-800-TEST-HELP",
        "real_number": "1800-599-0019",
        "available": "24/7",
    },
    {
        "name": "Vandrevala Foundation (Demo)",
        "number": "+91-99999-DEMO",
        "real_number": "9999666555",
        "available": "24/7",
        "whatsapp": True,
    },
    {
        "name": "Emergency Services (Demo)",
        "number": "911-DEMO",
        "real_number": "112",
        "available": "24/7",
        "note": "Police/Ambulance",
    },
]

@router.get("/crisis-info")
async def crisis_info():
    """Return crisis helpline information."""
    return {
        "crisis": True,
        "message": "We're really concerned about you right now. You're not alone.",
        "helplines": DEMO_HELPLINES,
        "banner": "⚠️ DEMO MODE — These are test numbers. Real version uses actual helplines.",
        "stay_option": "I'm here while you call",
    }
