import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import html2pdf from 'html2pdf.js/dist/html2pdf.bundle.min.js';
import "./OutputPage.css";
import logo from '../assets/react.svg';

const OutputPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [formattedResponse, setFormattedResponse] = useState("");
  const [projectTitle, setProjectTitle] = useState("Project Plan");
  const [userName, setUserName] = useState("Project Manager");
  const [companyName, setCompanyName] = useState("Company Name");
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    if (!location.state?.response) {
      navigate('/');
      return;
    }
    
    // First clean up the response to remove any existing table of contents
    let cleanResponse = location.state.response;
    
    // Clean up section titles and ensure each section triggers a page break
    cleanResponse = cleanResponse.replace(/##\s+(.*?)(?=##|$)/gs, (match, section) => {
      const sectionContent = section.trim();
      // Add a page break before each section
      return `<div class="html2pdf__page-break"></div><h2>${sectionContent}</h2>`;
    });
    
    // Special handling for sections without ## markup
    if (!cleanResponse.startsWith('<div class="html2pdf__page-break"></div>')) {
      cleanResponse = `<div class="html2pdf__page-break"></div>${cleanResponse}`;
    }
    
    // Basic formatting
    const formatted = cleanResponse
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .split('<br>')
      .map(line => {
        // Clean up the line
        line = line.trim();
        
        // Skip empty lines
        if (!line) return '';
        
        // Handle section headers without ## (like subsections)
        if (line.match(/^\d+\.\s[A-Z]/) && !line.startsWith('<h2>')) {
          return `<h3>${line}</h3>`;
        }
        
        // Handle subsections
        if (line.match(/^[A-Z][\w\s]+:/) && !line.startsWith('<h')) {
          return `<h4>${line}</h4>`;
        }
        
        // Handle bullet points
        if (line.startsWith('- ')) {
          return `<li>${line.substring(2)}</li>`;
        }
        
        // Handle numbered lists
        if (line.match(/^\d+\.\s/) && !line.match(/^\d+\.\s[A-Z]/)) {
          return `<li class="numbered">${line}</li>`;
        }
        
        // Regular paragraphs (if not already an HTML element)
        if (!line.startsWith('<')) {
          return `<p>${line}</p>`;
        }
        
        return line;
      })
      .filter(line => line) // Remove empty lines
      .join('');
    
    // Wrap lists properly
    let wrappedFormatted = formatted
      .replace(/<li>(?:(?!<li>).)*?<\/li>/gs, match => {
        if (match.includes('class="numbered"')) {
          return `<ol>${match}</ol>`;
        }
        return `<ul>${match}</ul>`;
      });
    
    // Clean up any double-wrapped lists
    wrappedFormatted = wrappedFormatted
      .replace(/<ul><ul>/g, '<ul>')
      .replace(/<\/ul><\/ul>/g, '</ul>')
      .replace(/<ol><ol>/g, '<ol>')
      .replace(/<\/ol><\/ol>/g, '</ol>');
    
    setFormattedResponse(wrappedFormatted);
  }, [location.state, navigate]);

  const handleDownload = () => {
    const content = document.getElementById('output-content');
    
    // Create a color theme
    const colors = {
      primary: '#000000',    // Changed to black
      secondary: '#000000',  // Changed to black
      accent: '#000000',     // Changed to black
      light: '#f8f9fa',
      dark: '#000000',       // Changed to black
      border: '#000000'      // Changed to black
    };
    
    // Create outer container
    const container = document.createElement('div');
    container.style.position = 'relative';
    container.style.color = colors.primary;  // Set default text color to blue
    
    // Create a stylish wrapper for PDF content
    const wrapper = document.createElement('div');
    wrapper.className = 'pdf-wrapper';
    wrapper.style.padding = '25px';
    wrapper.style.fontFamily = 'Roboto, Helvetica, Arial, sans-serif';
    wrapper.style.color = colors.primary;    // Set wrapper text color to blue
    wrapper.style.lineHeight = '1.6';
    wrapper.style.position = 'relative';
    
    // Add a subtle background
    wrapper.style.backgroundColor = '#ffffff';
    
    // Create cover page with adjusted styling
    const coverPage = document.createElement('div');
    coverPage.className = 'cover-page';
    coverPage.style.height = '842px'; // A4 height in pixels at 96 DPI
    coverPage.style.display = 'flex';
    coverPage.style.flexDirection = 'column';
    coverPage.style.justifyContent = 'center';
    coverPage.style.alignItems = 'center';
    coverPage.style.textAlign = 'center';
    coverPage.style.padding = '40px 20px';
    coverPage.style.position = 'relative';
    coverPage.style.border = `1px solid ${colors.border}`;
    coverPage.style.borderRadius = '5px';
    coverPage.style.margin = '0';
    coverPage.style.backgroundColor = '#ffffff';
    
    // Simplified background design
    coverPage.style.backgroundImage = `
      radial-gradient(circle at 50% 50%, rgba(26, 115, 232, 0.03) 0%, rgba(255, 255, 255, 0) 70%)
    `;
    
    // Add logo to cover with adjusted size
    const coverLogo = document.createElement('img');
    coverLogo.src = logo;
    coverLogo.alt = 'Logo';
    coverLogo.style.width = '60px';
    coverLogo.style.height = 'auto';
    coverLogo.style.marginBottom = '20px';
    coverPage.appendChild(coverLogo);
    
    // Add title to cover with adjusted spacing
    const coverTitle = document.createElement('h1');
    coverTitle.textContent = projectTitle;
    coverTitle.style.fontSize = '32px';
    coverTitle.style.fontWeight = '700';
    coverTitle.style.color = colors.primary;
    coverTitle.style.margin = '0 0 15px 0';
    coverTitle.style.textTransform = 'uppercase';
    coverTitle.style.letterSpacing = '1px';
    coverPage.appendChild(coverTitle);
    
    // Add subtitle with reduced margins
    const coverSubtitle = document.createElement('p');
    coverSubtitle.textContent = 'Comprehensive Project Documentation';
    coverSubtitle.style.fontSize = '16px';
    coverSubtitle.style.fontWeight = '300';
    coverSubtitle.style.color = colors.secondary;
    coverSubtitle.style.margin = '0 0 30px 0';
    coverPage.appendChild(coverSubtitle);
    
    // Smaller divider with reduced margins
    const divider = document.createElement('div');
    divider.style.width = '80px';
    divider.style.height = '2px';
    divider.style.background = colors.accent;
    divider.style.margin = '0 0 30px 0';
    coverPage.appendChild(divider);
    
    // Create info container for better organization
    const infoContainer = document.createElement('div');
    infoContainer.style.display = 'flex';
    infoContainer.style.flexDirection = 'column';
    infoContainer.style.gap = '8px';
    infoContainer.style.marginTop = '10px';
    
    // Add prepared by with consistent styling
    const preparedBy = document.createElement('div');
    preparedBy.style.fontSize = '13px';
    preparedBy.innerHTML = `<span style="color: ${colors.secondary};">Prepared by:</span> <strong>${userName}</strong>`;
    infoContainer.appendChild(preparedBy);
    
    // Add company with consistent styling
    const company = document.createElement('div');
    company.style.fontSize = '13px';
    company.innerHTML = `<span style="color: ${colors.secondary};">Company:</span> <strong>${companyName}</strong>`;
    infoContainer.appendChild(company);
    
    // Add date with consistent styling
    const date = document.createElement('div');
    date.style.fontSize = '13px';
    date.innerHTML = `<span style="color: ${colors.secondary};">Date:</span> <strong>${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</strong>`;
    infoContainer.appendChild(date);
    
    coverPage.appendChild(infoContainer);
    
    // Add the cover page to wrapper
    wrapper.appendChild(coverPage);
    
    // Create table of contents with improved styling
    const toc = document.createElement('div');
    toc.style.marginBottom = '30px';
    toc.style.padding = '30px';
    toc.style.backgroundColor = '#ffffff';
    toc.style.borderRadius = '5px';
    toc.style.border = `1px solid ${colors.border}`;
    toc.style.pageBreakBefore = 'always';
    toc.style.pageBreakAfter = 'always';
    toc.style.minHeight = '842px'; // A4 height to ensure proper page break
    
    const tocTitle = document.createElement('h2');
    tocTitle.textContent = 'Table of Contents';
    tocTitle.style.fontSize = '24px';
    tocTitle.style.marginTop = '0';
    tocTitle.style.marginBottom = '30px';
    tocTitle.style.color = colors.primary;
    tocTitle.style.borderBottom = `2px solid ${colors.accent}`;
    tocTitle.style.paddingBottom = '15px';
    toc.appendChild(tocTitle);
    
    // Create the tocList with improved styling
    const tocList = document.createElement('ul');
    tocList.style.listStyleType = 'none';
    tocList.style.padding = '0';
    tocList.style.margin = '0';
    tocList.style.display = 'flex';
    tocList.style.flexDirection = 'column';
    tocList.style.gap = '12px';

    // Modify the heading processing
    const headings = content.cloneNode(true).querySelectorAll('h2, h3');
    
    if (headings.length > 0) {
      headings.forEach((heading, index) => {
        const item = document.createElement('li');
        item.style.margin = '0';
        item.style.padding = '8px 0';
        item.style.display = 'flex';
        item.style.alignItems = 'center';
        item.style.gap = '8px';
        
        const link = document.createElement('a');
        link.textContent = heading.textContent;
        link.style.color = heading.tagName === 'H2' ? colors.primary : colors.secondary;
        link.style.textDecoration = 'none';
        link.style.fontWeight = heading.tagName === 'H2' ? '600' : '400';
        link.style.fontSize = heading.tagName === 'H2' ? '16px' : '14px';
        link.style.flex = '0 0 auto';
        link.style.maxWidth = '70%';
        link.style.whiteSpace = 'nowrap';
        link.style.overflow = 'hidden';
        link.style.textOverflow = 'ellipsis';
        
        // Indent H3s with more spacing
        if (heading.tagName === 'H3') {
          link.style.paddingLeft = '25px';
          link.style.position = 'relative';
          
          // Add bullet for H3 items
          const bullet = document.createElement('span');
          bullet.textContent = '•';
          bullet.style.position = 'absolute';
          bullet.style.left = '10px';
          bullet.style.color = colors.secondary;
          link.appendChild(bullet);
        }
        
        const dots = document.createElement('span');
        dots.style.flex = '1';
        dots.style.borderBottom = `1px dotted ${colors.border}`;
        dots.style.margin = '0 8px';
        
        const pageNum = document.createElement('span');
        pageNum.textContent = `${index + 3}`; // +3 for cover and TOC pages
        pageNum.style.color = colors.secondary;
        pageNum.style.fontSize = '14px';
        pageNum.style.flex = '0 0 auto';
        
        item.appendChild(link);
        item.appendChild(dots);
        item.appendChild(pageNum);
        tocList.appendChild(item);
        
        // Add ID to the heading for potential linking
        heading.id = `section-${index + 1}`;
      });
    }
    
    toc.appendChild(tocList);

    // Add spacing after TOC
    const tocSpacer = document.createElement('div');
    tocSpacer.style.height = '50px';
    toc.appendChild(tocSpacer);

    wrapper.appendChild(toc);
    
    // Main content with styled sections
    const mainContent = document.createElement('div');
    mainContent.className = 'main-content';
    
    // Process and enhance the content
    const enhancedContent = content.cloneNode(true);
    
    // Style headings
    enhancedContent.querySelectorAll('h1, h2, h3, h4').forEach((heading) => {
      heading.style.color = colors.primary;  // All headings in blue
      if (heading.tagName === 'H1') {
        heading.style.borderBottom = `2px solid ${colors.primary}`;
      } else if (heading.tagName === 'H2') {
        heading.style.borderBottom = `1px solid ${colors.primary}`;
      }
    });
    
    // Style paragraphs
    enhancedContent.querySelectorAll('p').forEach(paragraph => {
      paragraph.style.color = colors.primary;  // All paragraph text in blue
    });
    
    // Style lists
    enhancedContent.querySelectorAll('ul, ol').forEach(list => {
      list.style.margin = '15px 0';
      list.style.paddingLeft = '20px';
      
      if (list.tagName === 'UL') {
        list.style.listStyleType = 'none';
      } else {
        list.style.listStyleType = 'decimal';
      }
    });
    
    enhancedContent.querySelectorAll('li').forEach(item => {
      item.style.color = colors.primary;  // List items in blue
      item.style.margin = '8px 0';
      item.style.position = 'relative';
      
      // Style based on list type
      if (item.parentElement.tagName === 'UL') {
        item.style.paddingLeft = '20px';
        item.style.position = 'relative';
        
        // Add custom bullet points
        const bullet = document.createElement('span');
        bullet.innerHTML = '•';
        bullet.style.position = 'absolute';
        bullet.style.left = '0';
        bullet.style.color = colors.primary;  // Bullets in blue
        bullet.style.fontWeight = 'bold';
        bullet.style.fontSize = '18px';
        
        item.insertBefore(bullet, item.firstChild);
      }
    });
    
    // Add highlighting to important content
    enhancedContent.querySelectorAll('strong').forEach(strong => {
      strong.style.color = colors.primary;
      strong.style.fontWeight = 'bold';
    });
    
    enhancedContent.querySelectorAll('em').forEach(em => {
      em.style.color = colors.secondary;
    });
    
    mainContent.appendChild(enhancedContent);
    wrapper.appendChild(mainContent);
    
    // Create footer only with page numbers
    const footer = document.createElement('div');
    footer.style.marginTop = '20px';
    footer.style.paddingTop = '10px';
    footer.style.display = 'flex';
    footer.style.justifyContent = 'flex-end';
    
    const pageNumbers = document.createElement('div');
    pageNumbers.innerHTML = 'Page <span class="pageNumber"></span> of <span class="totalPages"></span>';
    pageNumbers.style.fontSize = '10px';
    pageNumbers.style.color = colors.secondary;

    footer.appendChild(pageNumbers);
    wrapper.appendChild(footer);
    
    // Add the wrapper to the container
    container.appendChild(wrapper);
    
    // PDF generation options
    const opt = {
      margin: [15, 15, 15, 15],
      filename: `${projectTitle.toLowerCase().replace(/\s+/g, '-')}.pdf`,
      image: { type: 'jpeg', quality: 1 },
      html2canvas: { 
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#FFFFFF'
      },
      jsPDF: { 
        unit: 'mm', 
        format: 'a4', 
        orientation: 'portrait', 
        compress: true 
      },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    };

    // Generate PDF with page numbers
    html2pdf().from(container).set(opt).toPdf().get('pdf').then(async (pdf) => {
      const totalPages = pdf.internal.getNumberOfPages();
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      // Add page numbers
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i);
        
        // Skip page number on cover page
        if (i === 1) continue;
        
        // Add page numbers in black
        pdf.setFontSize(9);
        pdf.setTextColor(0, 0, 0);  // Changed to black (RGB values)
        pdf.text(
          `Page ${i} of ${totalPages}`,
          pageWidth - 25,
          pageHeight - 10
        );
      }

      // Save the PDF
      pdf.save(`${projectTitle.toLowerCase().replace(/\s+/g, '-')}.pdf`);
    });
  };

  const handleBack = () => {
    navigate('/');
  };

  const handleSettingsToggle = () => {
    setShowSettings(!showSettings);
  };

  if (!formattedResponse) {
    return <div>Loading...</div>;
  }

  return (
    <div className="output-container">
      <div className="output-header">
        <h1 className="output-title">Project Plan Preview</h1>
        <div>
          <button onClick={handleSettingsToggle} className="settings-btn" style={{marginRight: '10px', backgroundColor: '#fbbc04'}}>
            <span>PDF Settings</span>
          </button>
          <button onClick={handleBack} className="back-btn" style={{marginRight: '10px', backgroundColor: '#5f6368'}}>
            <span>Back</span>
          </button>
          <button onClick={handleDownload} className="download-btn" style={{backgroundColor: '#1a73e8'}}>
            <span>Generate PDF</span>
          </button>
        </div>
      </div>
      
      {showSettings && (
        <div className="pdf-settings" style={{
          padding: '15px',
          marginBottom: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '5px',
          border: '1px solid #dadce0'
        }}>
          <h3 style={{margin: '0 0 15px 0', color: '#202124'}}>PDF Document Settings</h3>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '15px'}}>
            <div style={{flex: '1', minWidth: '200px'}}>
              <label style={{display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '14px'}}>
                Document Title:
              </label>
              <input 
                type="text" 
                value={projectTitle} 
                onChange={(e) => setProjectTitle(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #dadce0',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
            <div style={{flex: '1', minWidth: '200px'}}>
              <label style={{display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '14px'}}>
                Prepared By:
              </label>
              <input 
                type="text" 
                value={userName} 
                onChange={(e) => setUserName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #dadce0',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
            <div style={{flex: '1', minWidth: '200px'}}>
              <label style={{display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '14px'}}>
                Company Name:
              </label>
              <input 
                type="text" 
                value={companyName} 
                onChange={(e) => setCompanyName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #dadce0',
                  borderRadius: '4px',
                  fontSize: '14px'
                }}
              />
            </div>
          </div>
        </div>
      )}
      
      <div 
        id="output-content"
        className="output-content"
        dangerouslySetInnerHTML={{ __html: formattedResponse }}
      />
    </div>
  );
};

export default OutputPage;